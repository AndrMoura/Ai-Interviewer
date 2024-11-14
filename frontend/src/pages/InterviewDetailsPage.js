import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AdminSidebar from '../components/PageSidebar';
import { Button } from 'flowbite-react';

const InterviewDetailsPage = () => {
  const { session_id } = useParams();
  const [interview, setInterview] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchInterviewDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/interviews/${session_id}`);
        const data = await response.json();
        setInterview(data);
      } catch (error) {
        console.error("Failed to fetch interview details", error);
      }
    };
    fetchInterviewDetails();
  }, [session_id]);

  if (!interview) {
    return (
      <div className="flex h-screen bg-gray-100">
        <AdminSidebar />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-500">Loading interview details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <AdminSidebar />

      {/* Main content area */}
      <div className="flex-1 p-8 overflow-y-auto">
        <Button onClick={() => navigate('/admin/interviews')} className="mb-4 bg-indigo-500 hover:bg-indigo-600 text-white rounded-md">
          Back to Rated Interviews
        </Button>
        
        <header className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-indigo-700">Interview Details</h1>
          <p className="text-gray-600">Session ID: {session_id}</p>
        </header>

        <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Interview Transcript</h2>
          <div className="space-y-4">
            {interview.messages.map((msg, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg ${msg.role === 'AI' ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-800'}`}
              >
                <p className="font-semibold">{msg.role === 'AI' ? 'Interviewer' : 'Candidate'}:</p>
                <p>{msg.message}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Evaluation</h2>
          <p className="text-gray-700 whitespace-pre-line">{interview.evaluation}</p>
        </div>
      </div>
    </div>
  );
};

export default InterviewDetailsPage;
