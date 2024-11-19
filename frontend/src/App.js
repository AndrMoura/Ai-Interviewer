import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import InterviewSettingsPage from './pages/InterviewSettingsPage';
import InterviewPage from './pages/InterviewPage';
import AdminInterviewSettingsPage from './pages/AdminInterviewSettingsPage';
import CongratulationsPage from './pages/CongratulationsPage';
import RatedInterviewsPage from './pages/RatedInterviewListPage';
import InterviewDetailsPage from './pages/InterviewDetailsPage';
import RolesListingPage from './pages/RolesListingPage';
import EditRolePage from './pages/EditRolePage';
import { useAuth } from './hooks/useAuth';

// ProtectedRoute component to check if the user is authenticated
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  
  if (!token) {
    return <Navigate to="/login" />;
  }
  return children;
};

// RoleProtectedRoute component to check if the user has the required role
const RoleProtectedRoute = ({ children, requiredRole }) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  const userRole = localStorage.getItem('userRole') || sessionStorage.getItem('userRole');

  if (!token) {
    return <Navigate to="/login" />;
  }

  if (requiredRole && userRole !== requiredRole) {
    return <Navigate to="/settings" />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  
  if (token) {
    return <Navigate to="/settings" />;
  }
  return children;
};

const App = () => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to={user ? "/settings" : "/login"} />} />

        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <InterviewSettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interview"
          element={
            <ProtectedRoute>
              <InterviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path='/congratulations'
          element={
            <ProtectedRoute>
              <CongratulationsPage />
          </ProtectedRoute>
        }
        />
        <Route
          path="/admin/create-role"
          element={
            <RoleProtectedRoute requiredRole="admin">
              <AdminInterviewSettingsPage />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="/admin/roles"
          element={
            <RoleProtectedRoute requiredRole="admin">
              <RolesListingPage />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="/admin/role/:role"
          element={
            <RoleProtectedRoute requiredRole="admin">
              <EditRolePage />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="/admin/interviews"
          element={
            <RoleProtectedRoute requiredRole="admin">
              <RatedInterviewsPage />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="/admin/interview/:session_id"
          element={
            <RoleProtectedRoute requiredRole="admin">
              <InterviewDetailsPage />
            </RoleProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/settings" />} />
      </Routes>
    </Router>
  );
};

export default App;
