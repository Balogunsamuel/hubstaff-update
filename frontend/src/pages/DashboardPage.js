import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { DashboardWidget } from "../components/DashboardWidget";
import { Avatar } from "../components/Avatar";
import { analyticsAPI, usersAPI, projectsAPI } from "../api/client";

export const DashboardPage = ({ user, onLogout }) => {
  const [dashboardData, setDashboardData] = useState({
    widgets: [],
    teamActivity: [],
    recentProjects: []
  });
  const [loading, setLoading] = useState(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const toggleMobileSidebar = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  const closeMobileSidebar = () => {
    setIsMobileSidebarOpen(false);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsResponse, usersResponse, projectsResponse] = await Promise.all([
        analyticsAPI.getDashboardAnalytics(),
        usersAPI.getUsers({ limit: 10 }),
        projectsAPI.getProjects({ limit: 5 })
      ]);

      const analytics = analyticsResponse.data;
      const users = usersResponse.data;
      const projects = projectsResponse.data;

      console.log('Dashboard data fetched:', { analytics, users, projects }); // Debug log
      
      const widgets = [
        { title: "Hours Worked", value: `${(analytics.user_stats?.total_hours || 0).toFixed(2)}h`, subtitle: "This month", icon: "⏰", color: "blue" },
        { title: "Active Workers", value: users.filter(u => u.status === 'active').length, subtitle: "Right now", icon: "👥", color: "green" },
        { title: "Projects", value: projects.length, subtitle: "Active projects", icon: "📁", color: "purple" },
        { title: "Activity Level", value: `${Math.round(analytics.user_stats?.avg_activity || 0)}%`, subtitle: "This week", icon: "📊", color: "orange" },
      ];

      setDashboardData({
        widgets,
        teamActivity: users,
        recentProjects: projects
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <Header 
          user={user} 
          onLogout={onLogout} 
          currentPage="Dashboard" 
          onToggleMobileSidebar={toggleMobileSidebar}
          isMobileSidebarOpen={isMobileSidebarOpen}
        />
        <div className="flex">
          <Sidebar 
            currentPage="Dashboard" 
            isMobileOpen={isMobileSidebarOpen}
            onCloseMobile={closeMobileSidebar}
          />
          <main className="flex-1 lg:ml-64 p-4 sm:p-6 lg:p-8">
            <div className="max-w-7xl mx-auto">
              <div className="flex items-center justify-center h-64">
                <div className="flex flex-col items-center space-y-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
                  <p className="text-gray-600 text-sm">Loading your dashboard...</p>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Header 
        user={user} 
        onLogout={onLogout} 
        currentPage="Dashboard" 
        onToggleMobileSidebar={toggleMobileSidebar}
        isMobileSidebarOpen={isMobileSidebarOpen}
      />
      <div className="flex">
        <Sidebar 
          currentPage="Dashboard" 
          isMobileOpen={isMobileSidebarOpen}
          onCloseMobile={closeMobileSidebar}
        />
        
        <main className="flex-1 lg:ml-64 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Enhanced Header Section */}
            <div className="mb-8 relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5 rounded-2xl"></div>
              <div className="relative bg-white/70 backdrop-blur-sm rounded-2xl p-6 border border-white/20 shadow-lg">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <span className="text-white text-xl">📊</span>
                  </div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Dashboard
                  </h1>
                </div>
                <p className="text-gray-600 text-lg">
                  Welcome back, <span className="font-semibold text-blue-600">{user.name}</span>! Here's what's happening with your team today.
                </p>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {dashboardData.widgets.map((widget, index) => (
                <DashboardWidget key={index} {...widget} />
              ))}
            </div>

            {/* Enhanced Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Team Activity Card */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-green-600/10 to-emerald-600/10 rounded-2xl transform group-hover:scale-105 transition-transform duration-200"></div>
                <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-white/20">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm">👥</span>
                    </div>
                    <h3 className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                      Team Activity
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {dashboardData.teamActivity.slice(0, 4).map((user, index) => (
                      <div key={user.id} className="group/item hover:bg-green-50/50 rounded-xl p-3 transition-colors duration-200">
                        <div className="flex items-center space-x-4">
                          <div className="relative">
                            <Avatar user={user} size="md" />
                            <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
                              user.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                            }`}></div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-semibold text-gray-900 group-hover/item:text-green-700">{user.name}</h4>
                              <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                                user.status === 'active' 
                                  ? 'bg-green-100 text-green-800 border border-green-200' 
                                  : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                              }`}>
                                {user.status}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 capitalize">{user.role}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recent Projects Card */}
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 rounded-2xl transform group-hover:scale-105 transition-transform duration-200"></div>
                <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-white/20">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <span className="text-white text-sm">📁</span>
                    </div>
                    <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Recent Projects
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {dashboardData.recentProjects.map((project, index) => (
                      <div key={project.id} className="group/item hover:bg-blue-50/50 rounded-xl p-3 transition-colors duration-200">
                        <div className="border-l-4 border-gradient-to-b from-blue-500 to-purple-600 pl-4 relative">
                          <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full"></div>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-gray-900 group-hover/item:text-blue-700">{project.name}</h4>
                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                              project.status === 'active' 
                                ? 'bg-green-100 text-green-800 border border-green-200' 
                                : 'bg-gray-100 text-gray-800 border border-gray-200'
                            }`}>
                              {project.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-1">{project.client}</p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">⏱️</span>
                            <p className="text-sm font-medium text-blue-600">{(project.hours_tracked || 0).toFixed(2)} hours tracked</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};