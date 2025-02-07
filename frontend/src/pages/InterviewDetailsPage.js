import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import config from '../config';
import { useParams, useNavigate } from 'react-router-dom';
import AdminSidebar from '../components/PageSidebar';
import { Button, Select } from 'flowbite-react';

const InterviewDetailsPage = () => {
  const { session_id } = useParams();
  const [interview, setInterview] = useState(null);
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const fetchInterviewDetails = async () => {
      try {
        const response = await fetch(`${config.API_BASE_URL}/interviews/${session_id}`);
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

  const indexOfLastMessage = currentPage * itemsPerPage;
  const indexOfFirstMessage = indexOfLastMessage - itemsPerPage;
  const currentMessages = interview?.messages.slice(indexOfFirstMessage, indexOfLastMessage);
  const totalPages = Math.ceil((interview?.messages.length || 0) / itemsPerPage);

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
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-800">Interview Transcript</h2>
            <div className="flex items-center gap-4">
              <Select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
              >
                <option value="3">3 per page</option>
                <option value="10">10 per page</option>
                <option value="20">20 per page</option>
                <option value="50">50 per page</option>
              </Select>
            </div>
          </div>

          <div className="space-y-4">
            {currentMessages.map((msg, index) => (
              <div
                key={indexOfFirstMessage + index}
                className={`p-4 rounded-lg ${msg.role === 'AI' ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-800'}`}
              >
                <p className="font-semibold">{msg.role === 'AI' ? 'Interviewer' : 'Candidate'}:</p>
                <p>{msg.message}</p>
              </div>
            ))}
          </div>

          {/* Pagination controls */}
          <div className="flex justify-between items-center mt-4">
            <div className="text-sm text-gray-600">
              Showing {indexOfFirstMessage + 1} to {Math.min(indexOfLastMessage, interview.messages.length)} of {interview.messages.length} messages
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <Button
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Evaluation</h2>
            <ReactMarkdown className="prose max-w-none">{interview.evaluation}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default InterviewDetailsPage;
