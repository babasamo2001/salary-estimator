// Import libraries
import React, { useState } from 'react';
import '../App.css';

// Define unique Job Titles
const JOB_TITLES = [
  "Account Manager", "Accountant", "Administrative Assistant", "Back end Developer",
  "Business Analyst", "Business Development Manager", "Business Intelligence Analyst",
  "CEO", "Chief Data Officer", "Chief Technology Officer", "Content Marketing Manager",
  "Copywriter", "Creative Director", "Customer Service Manager", "Customer Service Rep",
  "Customer Service Representative", "Customer Success Manager", "Customer Success Rep",
  "Data Analyst", "Data Entry Clerk", "Data Scientist", "Developer", "Digital Content Producer",
  "Digital Marketing Manager", "Director", "Director of Business Development",
  "Director of Data Science", "Director of Engineering", "Director of Finance",
  "Director of HR", "Director of Human Capital", "Director of Human Resources",
  "Director of Marketing", "Director of Operations", "Director of Product Management",
  "Director of Sales", "Director of Sales and Marketing", "Event Coordinator",
  "Financial Advisor", "Financial Analyst", "Financial Manager", "Front End Developer",
  "Front end Developer", "Full Stack Engineer", "Graphic Designer", "HR Generalist",
  "HR Manager", "Help Desk Analyst", "Human Resources Director", "IT Manager",
  "IT Support", "IT Support Specialist", "Junior Account Manager", "Junior Accountant",
  "Junior Advertising Coordinator", "Junior Business Analyst", "Junior Business Development Associate",
  "Junior Business Operations Analyst", "Junior Copywriter", "Junior Customer Support Specialist",
  "Junior Data Analyst", "Junior Data Scientist", "Junior Designer", "Junior Developer",
  "Junior Financial Advisor", "Junior Financial Analyst", "Junior HR Coordinator",
  "Junior HR Generalist", "Junior Marketing Analyst", "Junior Marketing Coordinator",
  "Junior Marketing Manager", "Junior Marketing Specialist", "Junior Operations Analyst",
  "Junior Operations Coordinator", "Junior Operations Manager", "Junior Product Manager",
  "Junior Project Manager", "Junior Recruiter", "Junior Research Scientist",
  "Junior Sales Representative", "Junior Social Media Manager", "Junior Social Media Specialist",
  "Junior Software Developer", "Junior Software Engineer", "Junior UX Designer",
  "Junior Web Designer", "Junior Web Developer", "Marketing Analyst", "Marketing Coordinator",
  "Marketing Manager", "Marketing Specialist", "Network Engineer", "Office Manager",
  "Operations Analyst", "Operations Director", "Operations Manager", "Principal Engineer",
  "Principal Scientist", "Product Designer", "Product Manager", "Product Marketing Manager",
  "Project Engineer", "Project Manager", "Public Relations Manager", "Recruiter",
  "Research Director", "Research Scientist", "Sales Associate", "Sales Director",
  "Sales Executive", "Sales Manager", "Sales Operations Manager", "Sales Representative",
  "Senior Account Executive", "Senior Account Manager", "Senior Accountant",
  "Senior Business Analyst", "Senior Business Development Manager", "Senior Consultant",
  "Senior Data Analyst", "Senior Data Engineer", "Senior Data Scientist", "Senior Engineer",
  "Senior Financial Advisor", "Senior Financial Analyst", "Senior Financial Manager",
  "Senior Graphic Designer", "Senior HR Generalist", "Senior HR Manager",
  "Senior HR Specialist", "Senior Human Resources Coordinator", "Senior Human Resources Manager",
  "Senior Human Resources Specialist", "Senior IT Consultant", "Senior IT Project Manager",
  "Senior IT Support Specialist", "Senior Manager", "Senior Marketing Analyst",
  "Senior Marketing Coordinator", "Senior Marketing Director", "Senior Marketing Manager",
  "Senior Marketing Specialist", "Senior Operations Analyst", "Senior Operations Coordinator",
  "Senior Operations Manager", "Senior Product Designer", "Senior Product Development Manager",
  "Senior Product Manager", "Senior Product Marketing Manager", "Senior Project Coordinator",
  "Senior Project Engineer", "Senior Project Manager", "Senior Quality Assurance Analyst",
  "Senior Research Scientist", "Senior Researcher", "Senior Sales Manager",
  "Senior Sales Representative", "Senior Scientist", "Senior Software Architect",
  "Senior Software Developer", "Senior Software Engineer", "Senior Training Specialist",
  "Senior UX Designer", "Social Media Manager", "Social Media Specialist",
  "Software Developer", "Software Engineer", "Software Engineer Manager",
  "Software Manager", "Software Project Manager", "Strategy Consultant",
  "Supply Chain Analyst", "Supply Chain Manager", "Technical Recruiter",
  "Technical Support Specialist", "Technical Writer", "Training Specialist",
  "UX Designer", "UX Researcher", "VP of Finance", "VP of Operations", "Web Developer"
];

// Populate salary form
export default function Home() {
  const [formData, setFormData] = useState({
    Education_Level: 'High School',
    Job_Title: 'Software Engineer',
    Years_of_Experience: ''
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

//Handle form submit event
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/predict";
     // Make API call to the FastAPI server
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          "Education Level": formData.Education_Level,
          "Job Title": formData.Job_Title,
          "Years of Experience": parseFloat(formData.Years_of_Experience)
        })
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction from server.");
      }

      const data = await response.json();
      setPrediction(data.estimated_salary);
    } catch (err) {
      console.error("Error:", err);
      setError("Could not connect to the backend service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Salary Estimator</h1>
      <form onSubmit={handleSubmit}>
        <label>Education Level:</label>
        <select name="Education_Level" value={formData.Education_Level} onChange={handleChange}>
          <option value="High School">High School</option>
          <option value="Bachelor's">Bachelor's</option>
          <option value="Master's">Master's</option>
          <option value="PhD">PhD</option>
        </select>

        <label>Job Title:</label>
        <select name="Job_Title" value={formData.Job_Title} onChange={handleChange}>
          {JOB_TITLES.map((title) => (
            <option key={title} value={title}>
              {title}
            </option>
          ))}
        </select>

        <label>Years of Experience:</label>
        <input
          type="number"
          step="0.1"
          name="Years_of_Experience"
          value={formData.Years_of_Experience}
          onChange={handleChange}
          min="0"
          max="50"
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Calculating..." : "Predict Salary"}
        </button>
      </form>

      {error && <div className="error-box" style={{ color: 'red', marginTop: '10px', textAlign: 'center' }}>{error}</div>}

      {prediction !== null && (
        <div className="result-box">
          <h2>Estimated Salary: ${prediction.toLocaleString()}</h2>
          <h4>Prediction is in the context of the data the model is trained on.</h4>
        </div>
      )}
    </div>
  );
}