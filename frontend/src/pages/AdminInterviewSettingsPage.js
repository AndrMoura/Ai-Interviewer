import React, { useState } from 'react';
import config from '../config';
import { Button, Textarea, TextInput } from 'flowbite-react';

import {AdminSidebar, CustomToast} from '../components'

const AdminInterviewSettingsPage = () => {
  const [role, setRole] = useState('');
  const [customQuestions, setCustomQuestions] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [toastConfig, setToastConfig] = useState(null);

  const handleSaveInterviewSettings = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/admin/create-role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role,
          customQuestions,
          jobDescription,
        }),
      });

      const data = await response.json();

      if (response.status === 200) {
        setToastConfig({
          message: "Created role successfully",
          iconType: "success",
        });
      } else {
        setToastConfig({
          message: "Error creating role",
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
          <h1 className="text-4xl font-bold text-indigo-600 mb-2">Create an Interview Role</h1>
        </div>

        <div className="w-[80%] max-w-[800px] p-6 shadow-lg rounded-lg bg-white">
          <div className="mb-6">
            <label htmlFor="role" className="block text-gray-700 font-medium mb-2">Enter the Role</label>
            <TextInput
              id="role"
              className="mb-6"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="Enter role (e.g., Data Scientist, Software Engineer)"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="customQuestions" className="block text-gray-700 font-medium mb-2">Enter Custom Questions</label>
            <Textarea
              id="customQuestions"
              value={customQuestions}
              onChange={(e) => setCustomQuestions(e.target.value)}
              rows={6}
              placeholder="Enter custom questions to ask during the interview"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="jobDescription" className="block text-gray-700 font-medium mb-2">Enter Job Description</label>
            <Textarea
              id="jobDescription"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={6}
              placeholder="Enter the job description for this role"
            />
          </div>

          {/* Save Button */}
          <Button onClick={handleSaveInterviewSettings} className="w-full">
            Create Role
          </Button>

        </div>
      </div>
      {toastConfig && (
          <CustomToast
            message={toastConfig.message}
            iconType={toastConfig.iconType}
            onDismiss={() => setToastConfig(null)}
          />
        )}
    </div>
  );
};

export default AdminInterviewSettingsPage;
