from src.models.schemas import ServiceType, UrgencyLevel
import math

BASE_PRICES = {
    ServiceType.MEDICAL_CHECKUP: 50,
    ServiceType.MEDICATION_ADMINISTRATION: 30,
    ServiceType.PHYSICAL_THERAPY: 70,
    ServiceType.PERSONAL_CARE: 40
}

URGENCY_MULTIPLIERS = {
    UrgencyLevel.LOW: 1.0, # 低紧急程度价格不变
    UrgencyLevel.NORMAL: 1.2, # 普通紧急程度价格增加20%
    UrgencyLevel.HIGH: 1.5, # 高紧急程度价格增加50%
    UrgencyLevel.EMERGENCY: 2.0 # 紧急情况价格翻倍
}

def calculate_fee(service_type: ServiceType, urgency: UrgencyLevel, distance_km: float):
    base_price = BASE_PRICES[service_type]
    urgency_multiplier = URGENCY_MULTIPLIERS[urgency]
    distance_fee = 2 * max(0, distance_km - 5)  # 超过5公里开始收费，每公里2元
    
    total_fee = (base_price * urgency_multiplier) + distance_fee
    return math.ceil(total_fee)  # 取整