import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  UserCircle,
  Settings,
  MapPin,
  Calendar,
  Pencil,
  X,
  Save,
} from "lucide-react";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editPassword, setEditPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem("user"));
    if (storedUser) {
      setUser(storedUser);
    } else {
      alert("You must be logged in to view your profile.");
      navigate("/login");
    }
  }, [navigate]);

  const handleSaveChanges = () => {
    if (!editName.trim()) {
      alert("Name cannot be empty.");
      return;
    }

    const updatedUser = {
      ...user,
      name: editName,
      password: editPassword || user.password,
    };

    localStorage.setItem("user", JSON.stringify(updatedUser));
    setUser(updatedUser);
    setIsEditing(false);
    alert("Profile updated successfully!");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-20 px-6">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white py-10 flex flex-col items-center justify-center relative">
          <UserCircle className="w-20 h-20 mb-4 text-white" />
          <h2 className="text-3xl font-bold">
            Welcome, {user.name ? user.name.split(" ")[0] : "Traveler"}!
          </h2>
          <p className="text-blue-100 mt-2">{user.email}</p>
          <button
            onClick={() => {
              setEditName(user.name);
              setEditPassword("");
              setIsEditing(true);
            }}
            className="absolute top-4 right-6 bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200"
          >
            <Pencil className="w-4 h-4" />
            Edit Info
          </button>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Account Info */}
          <section>
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-blue-600" />
              Account Details
            </h3>
            <div className="bg-gray-50 p-5 rounded-lg border border-gray-200">
              <p className="text-gray-700">
                <strong>Name:</strong> {user.name}
              </p>
              <p className="text-gray-700 mt-2">
                <strong>Email:</strong> {user.email}
              </p>
              <p className="text-gray-500 text-sm mt-3 italic">
                Password updates will be available once backend integration is
                complete.
              </p>
            </div>
          </section>

          {/* Saved Trips */}
          <section>
            <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              Saved Trips
            </h3>
            <div className="bg-gray-50 p-5 rounded-lg border border-gray-200 text-gray-600">
              <p className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-500" />
                You don’t have any trips saved yet.
              </p>
              <p className="mt-2">
                Start exploring and create your first adventure soon!
              </p>
            </div>
          </section>

          {/* Logout */}
          <div className="flex justify-end">
            <button
              onClick={() => {
                localStorage.removeItem("user");
                alert("Logged out successfully.");
                navigate("/");
              }}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded-xl shadow-lg w-96 p-6 relative">
            <button
              onClick={() => setIsEditing(false)}
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Edit Your Info
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-600 mb-2 text-sm">Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-2 text-sm">
                  New Password (optional)
                </label>
                <input
                  type="password"
                  value={editPassword}
                  onChange={(e) => setEditPassword(e.target.value)}
                  placeholder="Enter a new password"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setIsEditing(false)}
                className="px-5 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveChanges}
                className="px-5 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
