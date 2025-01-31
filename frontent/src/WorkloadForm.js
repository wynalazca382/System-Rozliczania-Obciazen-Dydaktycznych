import React, { useState } from 'react';

function WorkloadForm() {
  const [formData, setFormData] = useState({
    hours: '',
    group_type: 'wykład',
    employee_level: 'profesor'
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('http://127.0.0.1:8000/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    const data = await response.json();
    setResult(data.total_workload || 'Błąd!');
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>Liczba godzin:
          <input type="number" name="hours" value={formData.hours} onChange={handleChange} required />
        </label>

        <label>Typ grupy:
          <select name="group_type" value={formData.group_type} onChange={handleChange}>
            <option value="wykład">Wykład</option>
            <option value="ćwiczenia">Ćwiczenia</option>
            <option value="laboratorium">Laboratorium</option>
          </select>
        </label>

        <label>Stanowisko:
          <select name="employee_level" value={formData.employee_level} onChange={handleChange}>
            <option value="profesor">Profesor</option>
            <option value="adiunkt">Adiunkt</option>
            <option value="asystent">Asystent</option>
          </select>
        </label>

        <button type="submit">Oblicz</button>
      </form>

      {result !== null && <h2>Wynik: {result}</h2>}
    </div>
  );
}

export default WorkloadForm;
