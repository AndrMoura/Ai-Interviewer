import React, { useEffect, useState } from 'react';
import config from '../config';
import { Button, Textarea } from 'flowbite-react';
import AdminSidebar from '../components/PageSidebar';
import { useParams } from 'react-router-dom';
import CustomToast from '../components/CustomToast';

const RoleEditPage = () => {
  const { role } = useParams();
  const [customQuestions, setCustomQuestions] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [toastConfig, setToastConfig] = useState(null);

  useEffect(() => {
    const fetchRoleDetails = async () => {
      try {
        const response = await fetch(`${config.API_BASE_URL}/admin/roles/${role}`);
        const data = await response.json();
        if (response.status === 200) {
          setCustomQuestions(data.custom_questions || '');
          setJobDescription(data.job_description || '');
        } else {
          alert('Error fetching role details');
        }
      } catch (error) {
        alert('Error fetching role details');
      }
    };

    fetchRoleDetails();
  }, [role]);

  const handleSaveRoleSettings = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/admin/roles/${role}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          custom_questions: customQuestions,
          job_description: jobDescription,
        }),
      });

      const data = await response.json();

      if (response.status === 200) {
        setToastConfig({
          message: "Role updated successfully",
          iconType: "success",
        });
      } else {
        setToastConfig({
          message: "Error updating role",
          iconType: "error",
        });
      }
    } catch (error) {
      setToastConfig({
        message: "Error updating role",
        iconType: "error",
      });
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <AdminSidebar />

      {/* Main content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-indigo-600 mb-2">Edit Role: {role}</h1>
        </div>

        <div className="w-[80%] max-w-[800px] p-6 shadow-lg rounded-lg bg-white">
          {/* Custom Questions Section */}
          <div className="mb-6">
            <label htmlFor="customQuestions" className="block text-gray-700 font-medium mb-2">
              Enter Custom Questions
            </label>
            <Textarea
              id="customQuestions"
              value={customQuestions}
              onChange={(e) => setCustomQuestions(e.target.value)}
              rows={6}
              placeholder="Enter custom questions to ask during the interview"
            />
          </div>

          {/* Job Description Section */}
          <div className="mb-6">
            <label htmlFor="jobDescription" className="block text-gray-700 font-medium mb-2">
              Enter Job Description
            </label>
            <Textarea
              id="jobDescription"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={6}
              placeholder="Enter the job description for this role"
            />
          </div>

          <Button onClick={handleSaveRoleSettings} className="w-full">
            Save Changes
          </Button>
        </div>

        {toastConfig && (
          <CustomToast
            message={toastConfig.message}
            iconType={toastConfig.iconType}
            onDismiss={() => setToastConfig(null)}
          />
        )}
      </div>
    </div>
  );
};

export default RoleEditPage;
