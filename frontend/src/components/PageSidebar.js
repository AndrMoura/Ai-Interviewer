import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Sidebar } from 'flowbite-react';
import { HiUserAdd, HiArrowSmRight, HiLogout, HiDocumentText, HiOutlineClipboardList, HiMenuAlt2 } from 'react-icons/hi';
import { useAuth } from '../hooks/useAuth';

const PageSidebar = () => {
  const { user, logout, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isCollapsed, setIsCollapsed] = useState(() => {
    return JSON.parse(localStorage.getItem('isCollapsed')) || false;
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setIsCollapsed(prevState => {
      const newState = !prevState;
      localStorage.setItem('isCollapsed', JSON.stringify(newState));
      return newState;
    });
  };

  useEffect(() => {
    const savedState = JSON.parse(localStorage.getItem('isCollapsed'));
    if (savedState !== null) {
      setIsCollapsed(savedState);
    }
  }, []);

  if (loading) return null;

  return (
    <Sidebar collapsed={isCollapsed} aria-label="Admin Sidebar" className="transition-all duration-300 ease-in-out">
      <Sidebar.Items>
        <div className="flex items-center justify-between p-2 border-gray-200">
          <div className="flex items-center gap-2">
            <button
              onClick={toggleSidebar}
              className="rounded-lg hover:bg-gray-100"
            >
              <HiMenuAlt2 className="w-6 h-6" />
            </button>
            {!isCollapsed && (
              <span className="font-semibold text-gray-700">AI Interview</span>
            )}
          </div>
        </div>

        <Sidebar.ItemGroup>
          <Sidebar.Item 
            as={Link} 
            to="/settings" 
            icon={HiArrowSmRight}
            className={/\/settings/.test(location.pathname) ? 'bg-gray-200' : ''}
          >
            Start Interview
          </Sidebar.Item>

          {user?.role === 'admin' && (
            <>
              <Sidebar.Item 
                as={Link} 
                to="/admin/create-role" 
                icon={HiUserAdd}
                className={/\/admin\/create-roles?/.test(location.pathname) ? 'bg-gray-200' : ''}
              >
                Create Role
              </Sidebar.Item>

              <Sidebar.Item 
                as={Link} 
                to="/admin/roles" 
                icon={HiOutlineClipboardList}
                className={/\/admin\/roles?/.test(location.pathname) ? 'bg-gray-200' : ''}
              >
                Roles
              </Sidebar.Item>

              <Sidebar.Item 
                as={Link} 
                to="/admin/interviews" 
                icon={HiDocumentText}
                className={/\/admin\/interviews?/.test(location.pathname) ? 'bg-gray-200' : ''}
              >
                Rated Interviews
              </Sidebar.Item>
            </>
          )}
        </Sidebar.ItemGroup>
          
        <Sidebar.ItemGroup>
          <Sidebar.Item icon={HiLogout} onClick={handleLogout}>
            Logout
          </Sidebar.Item>
        </Sidebar.ItemGroup>
      </Sidebar.Items>
    </Sidebar>
  );
};

export default PageSidebar;
