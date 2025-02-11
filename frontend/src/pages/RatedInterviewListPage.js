import React, { useEffect, useState } from 'react';
import { Pagination } from "flowbite-react";
import { useNavigate } from 'react-router-dom';
import { Button } from 'flowbite-react';
import config from '../config';
import AdminSidebar from '../components/PageSidebar';

const RatedInterviewsPage = () => {
  const [interviews, setInterviews] = useState([]);
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 9;

  const indexOfLastInterview = currentPage * itemsPerPage;
  const indexOfFirstInterview = indexOfLastInterview - itemsPerPage;
  const currentInterviews = interviews.slice(indexOfFirstInterview, indexOfLastInterview);
  const totalPages = Math.ceil(interviews.length / itemsPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const response = await fetch(`${config.API_BASE_URL}/interviews/`);
        const data = await response.json();
        setInterviews(data);
      } catch (error) {
        console.error("Failed to fetch interviews", error);
      }
    };
    fetchInterviews();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100">
      <AdminSidebar />

      {/* Main content area */}
      <div className="flex-1 p-8">
      {interviews.length > 0 && (
        <header className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-indigo-700">Rated Interviews</h1>
          <p className="text-gray-600">Browse past interviews and their summaries</p>
        </header>
      )}

        {interviews.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              No Interviews Yet
            </h3>
            <p className="text-gray-500">
              Your completed interviews will appear here.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {currentInterviews.map((interview) => (
                <div
                  key={interview.session_id}
                  className="bg-white shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow duration-300 cursor-pointer"
                  onClick={() => navigate(`/admin/interview/${interview.session_id}`)}
                >
                  <h2 className="text-lg font-semibold text-gray-800 mb-2">
                    Session ID: {interview.session_id.slice(0, 15)}...
                  </h2>
                  <p className="text-gray-600 text-sm mb-4">
                    {interview.preview}...
                  </p>
                  <Button
                    onClick={() => navigate(`/interview/${interview.session_id}`)}
                    className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-md mt-4"
                  >
                    View Details
                  </Button>
                </div>
              ))}
            </div>

            <div className="flex justify-center mt-4 mb-8">
              <Pagination
                currentPage={currentPage}
                onPageChange={handlePageChange}
                totalPages={totalPages}
                showIcons={true}
                layout="table"
                previousLabel="Previous"
                nextLabel="Next"
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RatedInterviewsPage;
