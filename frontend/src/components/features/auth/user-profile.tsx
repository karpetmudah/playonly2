import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "#/components/shared/buttons/button";
import { Input } from "#/components/shared/inputs/input";
import { displayErrorToast, displaySuccessToast } from "#/utils/custom-toast-handlers";
import { I18nKey } from "#/i18n/declaration";
import OpenHands from "#/api/open-hands";

interface UserData {
  user_id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  credits: number;
  total_credits_purchased: number;
  total_credits_used: number;
  created_at: string;
  last_login?: string;
}

export function UserProfile() {
  const { t } = useTranslation();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const profile = await OpenHands.getUserProfile();
      setUserData(profile);
      setFormData({
        full_name: profile.full_name || "",
        email: profile.email,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || t(I18nKey.AUTH$PROFILE_LOAD_ERROR);
      displayErrorToast(errorMessage);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const updatedProfile = await OpenHands.updateUserProfile(formData);
      setUserData(updatedProfile);
      setIsEditing(false);
      displaySuccessToast(t(I18nKey.AUTH$PROFILE_UPDATE_SUCCESS));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || t(I18nKey.AUTH$PROFILE_UPDATE_ERROR);
      displayErrorToast(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCancel = () => {
    if (userData) {
      setFormData({
        full_name: userData.full_name || "",
        email: userData.email,
      });
    }
    setIsEditing(false);
  };

  if (!userData) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {t(I18nKey.AUTH$USER_PROFILE)}
        </h2>
        {!isEditing && (
          <Button
            onClick={() => setIsEditing(true)}
            variant="outline"
          >
            {t(I18nKey.AUTH$EDIT_PROFILE)}
          </Button>
        )}
      </div>

      {isEditing ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
              {t(I18nKey.AUTH$FULL_NAME)}
            </label>
            <Input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleInputChange}
              placeholder={t(I18nKey.AUTH$FULL_NAME_PLACEHOLDER)}
              className="w-full"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              {t(I18nKey.AUTH$EMAIL)}
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder={t(I18nKey.AUTH$EMAIL_PLACEHOLDER)}
              className="w-full"
            />
          </div>

          <div className="flex space-x-4">
            <Button
              type="submit"
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? t(I18nKey.AUTH$UPDATING) : t(I18nKey.AUTH$UPDATE_PROFILE)}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
              className="flex-1"
            >
              {t(I18nKey.AUTH$CANCEL)}
            </Button>
          </div>
        </form>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$FULL_NAME)}
              </label>
              <p className="text-gray-900">{userData.full_name || t(I18nKey.AUTH$NOT_PROVIDED)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$EMAIL)}
              </label>
              <p className="text-gray-900">{userData.email}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$ACCOUNT_STATUS)}
              </label>
              <div className="flex items-center space-x-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  userData.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {userData.is_active ? t(I18nKey.AUTH$ACTIVE) : t(I18nKey.AUTH$INACTIVE)}
                </span>
                {userData.is_verified && (
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    {t(I18nKey.AUTH$VERIFIED)}
                  </span>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$CREDITS_BALANCE)}
              </label>
              <p className="text-2xl font-bold text-green-600">${userData.credits.toFixed(2)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$TOTAL_PURCHASED)}
              </label>
              <p className="text-gray-900">${userData.total_credits_purchased.toFixed(2)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$TOTAL_USED)}
              </label>
              <p className="text-gray-900">${userData.total_credits_used.toFixed(2)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t(I18nKey.AUTH$MEMBER_SINCE)}
              </label>
              <p className="text-gray-900">
                {new Date(userData.created_at).toLocaleDateString()}
              </p>
            </div>

            {userData.last_login && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t(I18nKey.AUTH$LAST_LOGIN)}
                </label>
                <p className="text-gray-900">
                  {new Date(userData.last_login).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
