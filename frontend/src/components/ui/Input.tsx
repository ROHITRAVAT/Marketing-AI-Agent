import React, { forwardRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', label, error, helperText, icon, id, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-[11px] font-mono uppercase tracking-wider text-[#71717A]">
            {label}
          </label>
        )}
        <div className="relative rounded-xl shadow-2xs">
          {icon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[#A1A1AA]">
              {icon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            type={inputType}
            className={cn(
              'block w-full rounded-xl bg-[#F3F3EE] border text-[#18181B] text-xs sm:text-sm placeholder-[#A1A1AA] transition-all duration-150 outline-none',
              'focus:bg-white focus:ring-2 focus:ring-[#18181B]/10 focus:border-[#18181B]',
              icon ? 'pl-10' : 'pl-3.5',
              isPassword ? 'pr-10' : 'pr-3.5',
              'py-2.5',
              error
                ? 'border-rose-400 focus:border-rose-600 focus:ring-rose-500/20 text-rose-900 bg-rose-50/40'
                : 'border-[#E4E4DC] hover:border-[#D1D1C7]',
              className
            )}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#71717A] hover:text-[#18181B] transition-colors focus:outline-none"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          )}
        </div>
        {error && <p className="text-xs text-rose-600 mt-1">{error}</p>}
        {helperText && !error && <p className="text-xs text-[#71717A] mt-1">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
