import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { LoginForm } from "#/components/features/auth/login-form";
import { RegisterForm } from "#/components/features/auth/register-form";
import { I18nKey } from "#/i18n/declaration";

export default function AuthPage() {
  const { t } = useTranslation();
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <img
            className="h-12 w-auto"
            src="/logo.png"
            alt="OpenHands"
          />
        </div>
        <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {t(I18nKey.AUTH$WELCOME_TO_OPENHANDS)}
        </h1>
        <p className="mt-2 text-center text-sm text-gray-600">
          {t(I18nKey.AUTH$SUBTITLE)}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {isLogin ? (
            <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
          ) : (
            <RegisterForm onSwitchToLogin={() => setIsLogin(true)} />
          )}
        </div>
      </div>
    </div>
  );
}
