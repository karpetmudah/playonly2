import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { Button } from "#/components/shared/buttons/button";
import { Input } from "#/components/shared/inputs/input";
import { displayErrorToast, displaySuccessToast } from "#/utils/custom-toast-handlers";
import { I18nKey } from "#/i18n/declaration";
import OpenHands from "#/api/open-hands";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await OpenHands.login(formData);

      // Store token in localStorage
      localStorage.setItem("auth_token", response.access_token);
      localStorage.setItem("user_data", JSON.stringify(response.user));

      displaySuccessToast(t(I18nKey.AUTH$LOGIN_SUCCESS));

      if (onSuccess) {
        onSuccess();
      } else {
        navigate("/");
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || t(I18nKey.AUTH$LOGIN_ERROR);
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
        {t(I18nKey.AUTH$LOGIN_TITLE)}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
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

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            {t(I18nKey.AUTH$PASSWORD)}
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
        </div>

        <Button
          type="submit"
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? t(I18nKey.AUTH$LOGGING_IN) : t(I18nKey.AUTH$LOGIN)}
        </Button>
      </form>

      {onSwitchToRegister && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {t(I18nKey.AUTH$NO_ACCOUNT)}{" "}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              {t(I18nKey.AUTH$REGISTER)}
            </button>
          </p>
        </div>
      )}
    </div>
  );
}
