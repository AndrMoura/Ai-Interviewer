import React, { useEffect, useState } from "react";
import { Toast, ToastToggle } from "flowbite-react";
import { HiCheck, HiExclamation, HiX } from "react-icons/hi";

const iconMapping = {
  success: {
    icon: <HiCheck className="h-5 w-5" />,
    bgColor: "bg-green-100",
    textColor: "text-green-500",
    darkBgColor: "dark:bg-green-800",
    darkTextColor: "dark:text-green-200",
  },
  error: {
    icon: <HiX className="h-5 w-5" />,
    bgColor: "bg-red-100",
    textColor: "text-red-500",
    darkBgColor: "dark:bg-red-800",
    darkTextColor: "dark:text-red-200",
  },
  warning: {
    icon: <HiExclamation className="h-5 w-5" />,
    bgColor: "bg-orange-100",
    textColor: "text-orange-500",
    darkBgColor: "dark:bg-orange-700",
    darkTextColor: "dark:text-orange-200",
  },
};

const CustomToast = ({
  message,
  iconType = "success",
  duration = 5000, // auto-dismiss duration in milliseconds
  onDismiss, // callback when the toast is dismissed
}) => {
  const [visible, setVisible] = useState(true);

  const iconData = iconMapping[iconType] || iconMapping.success;

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setVisible(false);
        if (onDismiss) onDismiss();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onDismiss]);

  if (!visible) return null;

  return (
    <div className="fixed top-4 right-4 w-[300px] z-50">
      <Toast>
        <div
          className={`inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${iconData.bgColor} ${iconData.textColor} ${iconData.darkBgColor} ${iconData.darkTextColor}`}
        >
          {iconData.icon}
        </div>
        <div className="ml-3 text-sm font-normal">{message}</div>
        <ToastToggle
          onClick={() => {
            setVisible(false);
            if (onDismiss) onDismiss();
          }}
        />
      </Toast>
    </div>
  );
};

export default CustomToast;
