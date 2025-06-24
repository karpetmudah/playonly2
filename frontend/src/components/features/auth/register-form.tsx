import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { Button } from "#/components/shared/buttons/button";
import { Input } from "#/components/shared/inputs/input";
import { displayErrorToast, displaySuccessToast } from "#/utils/custom-toast-handlers";
import { I18nKey } from "#/i18n/declaration";
import OpenHands from "#/api/open-hands";

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export function RegisterForm({ onSuccess, onSwitchToLogin }: RegisterFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      displayErrorToast(t(I18nKey.AUTH$PASSWORD_MISMATCH));
      return;
    }

    if (formData.password.length < 8) {
      displayErrorToast(t(I18nKey.AUTH$PASSWORD_TOO_SHORT));
      return;
    }

    setIsLoading(true);

    try {
      const registrationData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      };

      const response = await OpenHands.register(registrationData);

      // Store token in localStorage
      localStorage.setItem("auth_token", response.access_token);
      localStorage.setItem("user_data", JSON.stringify(response.user));

      displaySuccessToast(t(I18nKey.AUTH$REGISTER_SUCCESS));

      if (onSuccess) {
        onSuccess();
      } else {
        navigate("/");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || t(I18nKey.AUTH$REGISTER_ERROR);
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

  return (
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-6">
        {t(I18nKey.AUTH$REGISTER_TITLE)}
      </h2>

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
            {t(I18nKey.AUTH$EMAIL)} *
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

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            {t(I18nKey.AUTH$PASSWORD)} *
          </label>
          <Input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            placeholder={t(I18nKey.AUTH$PASSWORD_PLACEHOLDER)}
            className="w-full"
          />
          <p className="text-xs text-gray-500 mt-1">
            {t(I18nKey.AUTH$PASSWORD_REQUIREMENTS)}
          </p>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
            {t(I18nKey.AUTH$CONFIRM_PASSWORD)} *
          </label>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            required
            placeholder={t(I18nKey.AUTH$CONFIRM_PASSWORD_PLACEHOLDER)}
            className="w-full"
          />
        </div>

        <Button
          type="submit"
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? t(I18nKey.AUTH$REGISTERING) : t(I18nKey.AUTH$REGISTER)}
        </Button>
      </form>

      {onSwitchToLogin && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {t(I18nKey.AUTH$HAVE_ACCOUNT)}{" "}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              {t(I18nKey.AUTH$LOGIN)}
            </button>
          </p>
        </div>
      )}
    </div>
  );
}
