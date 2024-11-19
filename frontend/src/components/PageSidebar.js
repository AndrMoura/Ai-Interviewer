import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sidebar } from 'flowbite-react';
import { HiUserAdd, HiArrowSmRight, HiLogout, HiDocumentText, HiOutlineClipboardList } from 'react-icons/hi';
import { useAuth } from '../hooks/useAuth';

const PageSidebar = () => {
  const { user, logout, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) return null;

  return (
    <Sidebar aria-label="Admin Sidebar">
      <Sidebar.Items>
        <Sidebar.ItemGroup>
          <Sidebar.Item as={Link} to="/settings" icon={HiArrowSmRight}>
            Start Interview
          </Sidebar.Item>

          {user?.role === 'admin' && (
            <>
              <Sidebar.Item as={Link} to="/admin/create-role" icon={HiUserAdd}>
              Create Role
              </Sidebar.Item>

              <Sidebar.Item as={Link} to="/admin/roles" icon={HiOutlineClipboardList}>
                Roles
              </Sidebar.Item>

              <Sidebar.Item as={Link} to="/admin/interviews" icon={HiDocumentText}>
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
