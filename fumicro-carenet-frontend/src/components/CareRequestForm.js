import React, { useState } from 'react';

function CareRequestForm() {
  const [formData, setFormData] = useState({
    requester_name: '',
    patient_name: '',
    address: '',
    service_type: '',
    urgency: '',
    description: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:3001/api/care-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        alert('Care request submitted successfully!');
        setFormData({
          requester_name: '',
          patient_name: '',
          address: '',
          service_type: '',
          urgency: '',
          description: ''
        });
      } else {
        alert('Failed to submit care request');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while submitting the care request');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="requester_name" value={formData.requester_name} onChange={handleChange} placeholder="Requester Name" required />
      <input name="patient_name" value={formData.patient_name} onChange={handleChange} placeholder="Patient Name" required />
      <input name="address" value={formData.address} onChange={handleChange} placeholder="Address" required />
      <select name="service_type" value={formData.service_type} onChange={handleChange} required>
        <option value="">Select Service Type</option>
        <option value="Medical Checkup">Medical Checkup</option>
        <option value="Medication Administration">Medication Administration</option>
        <option value="Physical Therapy">Physical Therapy</option>
        <option value="Personal Care">Personal Care</option>
      </select>
      <select name="urgency" value={formData.urgency} onChange={handleChange} required>
        <option value="">Select Urgency</option>
        <option value="Low">Low</option>
        <option value="Normal">Normal</option>
        <option value="High">High</option>
        <option value="Emergency">Emergency</option>
      </select>
      <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Description"></textarea>
      <button type="submit">Submit Care Request</button>
    </form>
  );
}

export default CareRequestForm;