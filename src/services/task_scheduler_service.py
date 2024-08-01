import json
from typing import List
from src.models.schemas import CareRequest, CareWorker
from src.services.care_worker_service import CareWorkerService
from src.services.care_request_service import CareRequestService
from src.services.distance_service import DistanceService
from src.utils.kafka_config import get_kafka_producer, get_kafka_consumer
from src.utils.redis_config import get_redis

class TaskSchedulerService:
    def __init__(self, care_worker_service: CareWorkerService, care_request_service: CareRequestService, distance_service: DistanceService):
        self.care_worker_service = care_worker_service
        self.care_request_service = care_request_service
        self.distance_service = distance_service

    async def assign_task(self, care_request_id: str):
        care_request = await self.care_request_service.get_care_request(care_request_id)
        
        # Publish task to Kafka
        async for producer in get_kafka_producer():
            await producer.send_and_wait("care_requests", json.dumps(care_request.dict()).encode())

    async def process_tasks(self):
        async for consumer in get_kafka_consumer("care_requests"):
            async for msg in consumer:
                care_request = CareRequest.parse_raw(msg.value)
                await self._process_single_task(care_request)

    async def _process_single_task(self, care_request: CareRequest):
        async for redis in get_redis():
            # Get nearby workers from Redis
            nearby_workers = await redis.georadius(
                "worker_locations", 
                care_request.location.longitude, 
                care_request.location.latitude, 
                10, 
                "km", 
                withcoord=True
            )

        if not nearby_workers:
            # Handle case when no workers are available
            return

        optimal_worker = await self._find_optimal_worker(care_request, nearby_workers)
        
        if optimal_worker:
            await self.care_request_service.assign_care_worker(care_request.id, optimal_worker.id)
        else:
            # Handle case when no suitable worker is found
            pass

    async def _find_optimal_worker(self, care_request: CareRequest, nearby_workers: List[tuple]) -> CareWorker:
        scored_workers = []
        for worker_id, (lon, lat) in nearby_workers:
            worker = await self.care_worker_service.get_care_worker(worker_id.decode())
            score = self._calculate_worker_score(care_request, worker)
            scored_workers.append((worker, score))

        scored_workers.sort(key=lambda x: x[1], reverse=True)
        return scored_workers[0][0] if scored_workers else None
    
    def _calculate_worker_score(self, care_request: CareRequest, worker: CareWorker) -> float:
        # Calculate distance score (inverse of distance)
        distance = self.distance_service.calculate_distance(care_request.location, worker.current_location)
        distance_score = 1 / (1 + distance)  # Normalize distance score

        # Calculate specialization match score
        specialization_score = 1 if care_request.service_type in worker.specializations else 0

        # Calculate availability score (can be more complex based on worker's schedule)
        availability_score = 1 if worker.status == "AVAILABLE" else 0

        # Weighted sum of scores
        total_score = (
            0.4 * distance_score +
            0.4 * specialization_score +
            0.2 * availability_score
        )

        return total_score

    async def schedule_new_request(self, care_request_id: str):
        await self.assign_task(care_request_id)

    async def update_worker_location(self, worker_id: str, latitude: float, longitude: float):
        async for redis in get_redis():
            await redis.geoadd("worker_locations", longitude, latitude, worker_id)