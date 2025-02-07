import React, { useState, useEffect } from 'react';
import config from '../config';
import { Button, Checkbox, Select, Textarea, FileInput, Spinner } from 'flowbite-react';
import { useNavigate,  } from 'react-router-dom';
import axios from 'axios';
import PageSidebar from '../components/PageSidebar';
import { CustomToast} from '../components'


const InterviewSettingsPage = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState('');
  const [roles, setRoles] = useState([]);
  const [jobDescription, setJobDescription] = useState('');
  const [portfolio, setPortfolio] = useState('');
  const [isPdf, setIsPdf] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [toastConfig, setToastConfig] = useState(null);

  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const handleStartInterview = async () => {
    const formData = new FormData();
    formData.append('role', role);
    formData.append('role_description', jobDescription);
  
    if (!isPdf && portfolio.trim() !== '') {
      formData.append('portfolio_text', portfolio);
    }
  
    if (isPdf && pdfFile) {
      formData.append('portfolio_file', pdfFile);
    }
  
    setIsLoading(true);

    try {
      const response = await fetch(`${config.API_BASE_URL}/start-interview`, {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const data = await response.json();
  
        navigate('/interview', { 
          state: { 
            audio_base64: data.audio_base64,
            session_id: data.session_id 
          }
        });
      } else {
        const data = await response.json();
        setToastConfig({
          message: data.detail,
          iconType: "error",
        });
      }
    } catch (error) {
      console.error('Error sending interview data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    axios.get(`${config.API_BASE_URL}/admin/roles`)
      .then(response => {
        setRoles(response.data.roles);
        if (response.data.roles.length > 0) {
          const firstRole = response.data.roles[0];
          setRole(firstRole.role);
          setJobDescription(firstRole.job_description);
        }
      })
      .catch(error => {
        console.error('Error fetching roles:', error);
      });
  }, []);

  const handleRoleChange = (e) => {
    const selectedRole = e.target.value;
    setRole(selectedRole);

    const selectedRoleDescription = roles.find(r => r.role === selectedRole)?.job_description || '';
    setJobDescription(selectedRoleDescription);
  };

  // Check if either the checkbox is checked or the Textarea has content
  const isButtonEnabled = isPdf || portfolio.trim() !== '';

  return (
    <div className="flex h-screen bg-gray-100">
      <PageSidebar />

      <div className="flex flex-col h-full items-center justify-center w-full px-6">
        <div className="w-full max-w-3xl p-6 shadow-lg rounded-lg bg-white">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold text-indigo-600 mb-2">Interview Settings</h1>
          </div>

          <div className="mb-6">
            <p className="text-gray-600 text-sm mb-2">Provide the portfolio or CV. You can either provide it as text or upload a PDF.</p>
            
            <div className="flex items-center mb-4">
              <Checkbox
                type="checkbox"
                id="isPdf"
                checked={isPdf}
                onChange={() => setIsPdf(!isPdf)}
                className="mr-2"
              />
              <label htmlFor="isPdf" className="text-gray-700">Upload Portfolio as PDF</label>
            </div>

            {isPdf ? (
              <div className="mb-6">
                <label htmlFor="pdfUpload" className="block text-gray-700 font-medium mb-2">Upload Portfolio/CV (PDF)</label>
                <FileInput
                  id="pdfUpload"
                  className="w-full"
                  onChange={handleFileChange}
                  accept=".pdf"
                />
              </div>
            ) : (
              <Textarea
                placeholder="Enter Portfolio or CV"
                rows={6}
                className="mb-6"
                value={portfolio}
                onChange={(e) => setPortfolio(e.target.value)}
              />
            )}
          </div>

          {/* Role Selection */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <label htmlFor="role" className="text-gray-700 font-medium">
                  Select the Role
                </label>
              </div>
              <button 
                onClick={() => role && navigate(`/admin/role/${role}`)}
                className="text-gray-500 hover:text-indigo-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
            </div>
            <Select
              id="role"
              className="mb-6"
              value={role}
              onChange={handleRoleChange}
            >
              {roles.map((roleItem, index) => (
                <option key={index} value={roleItem.role}>{roleItem.role}</option>
              ))}
            </Select>
          </div>

          {/* Job Description Section */}
          <div className="mb-6">
            <label htmlFor="jobDescription" className="block text-gray-700 font-medium mb-2">Job Description</label>
            <Textarea
              id="jobDescription"
              placeholder="Job description will appear here"
              rows={6}
              className="mb-6 bg-gray-200 text-gray-500 border border-gray-300 focus:ring-0 focus:border-gray-300 cursor-not-allowed"
              value={jobDescription}
              readOnly
            />
          </div>

          {/* Start Interview Button */}
          {isLoading ? (
            <div className="flex justify-center items-center space-x-3">
              <span className="text-gray-600">Loading Interview...</span>
              <Spinner aria-label="Interview is being prepared" />
            </div>
          ) : (
            <Button 
              onClick={handleStartInterview} 
              className="w-full"
              disabled={!isButtonEnabled}
            >
              Start Interview
            </Button>
          )}
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

export default InterviewSettingsPage;
