import { useMutation } from "@tanstack/react-query";
import { Trans, useTranslation } from "react-i18next";
import { I18nKey } from "#/i18n/declaration";
import AllHandsLogo from "#/assets/branding/all-hands-logo.svg?react";
import { ModalBackdrop } from "#/components/shared/modals/modal-backdrop";
import { ModalBody } from "#/components/shared/modals/modal-body";
import OpenHands from "#/api/open-hands";
import { BrandButton } from "../settings/brand-button";
import { displayErrorToast } from "#/utils/custom-toast-handlers";

interface SetupPaymentModalProps {
  onClose?: () => void;
}

export function SetupPaymentModal({ onClose }: SetupPaymentModalProps) {
  const { t } = useTranslation();
  const { mutate, isPending } = useMutation({
    mutationFn: OpenHands.createBillingSessionResponse,
    onSuccess: (data) => {
      window.location.href = data;
    },
    onError: () => {
      displayErrorToast(t(I18nKey.BILLING$ERROR_WHILE_CREATING_SESSION));
    },
  });

  return (
    <ModalBackdrop>
      <ModalBody className="border border-tertiary">
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close modal"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
        <AllHandsLogo width={68} height={46} />
        <div className="flex flex-col gap-2 w-full items-center text-center">
          <h1 className="text-2xl font-bold">
            {t(I18nKey.BILLING$YOUVE_GOT_50)}
          </h1>
          <p>
            <Trans
              i18nKey="BILLING$CLAIM_YOUR_50"
              components={{ b: <strong /> }}
            />
          </p>
        </div>
        <div className="flex flex-col gap-2 w-full">
          <BrandButton
            testId="proceed-to-stripe-button"
            type="submit"
            variant="primary"
            className="w-full"
            isDisabled={isPending}
            onClick={mutate}
          >
            {t(I18nKey.BILLING$PROCEED_TO_STRIPE)}
          </BrandButton>
          {onClose && (
            <BrandButton
              testId="skip-payment-button"
              type="button"
              variant="secondary"
              className="w-full"
              onClick={onClose}
            >
              {t(I18nKey.BILLING$SKIP_FOR_NOW)}
            </BrandButton>
          )}
        </div>
      </ModalBody>
    </ModalBackdrop>
  );
}
