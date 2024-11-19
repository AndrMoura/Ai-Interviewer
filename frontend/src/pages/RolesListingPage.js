import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'flowbite-react';
import config from '../config';
import AdminSidebar from '../components/PageSidebar';

const RolesListingPage = () => {
  const [roles, setRoles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await fetch(`${config.API_BASE_URL}/admin/roles`);
        const data = await response.json();
        setRoles(data.roles);
      } catch (error) {
        console.error("Failed to fetch roles", error);
      }
    };
    fetchRoles();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100">
      <AdminSidebar />

      {/* Main content area */}
      <div className="flex-1 p-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-indigo-700">Roles</h1>
          <p className="text-gray-600">Browse available roles and their descriptions</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div
              key={role.role}
              className="bg-white shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow duration-300 cursor-pointer"
              onClick={() => navigate(`/admin/role/${role.role}`)}
            >
              <h2 className="text-lg font-semibold text-gray-800 mb-2">
                Role: {role.role}
              </h2>
              <p className="text-gray-600 text-sm mb-4">
                {role.job_description || "No description available"}...
              </p>
              <Button
                onClick={() => navigate(`/admin/role/${role.role}`)}
                className="w-full bg-indigo-500 hover:bg-indigo-600 text-white rounded-md mt-4"
              >
                View Details
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RolesListingPage;
