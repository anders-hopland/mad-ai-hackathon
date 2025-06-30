'use client';

import { ReactNode } from 'react';

interface CardProps {
  title?: string | ReactNode;
  subtitle?: string | ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
  bordered?: boolean;
  compact?: boolean;
}

export default function Card({ 
  title, 
  subtitle, 
  children, 
  footer, 
  className = '',
  bordered = true,
  compact = false
}: CardProps) {
  return (
    <div className={`card bg-base-100 shadow-md ${bordered ? 'border border-base-300' : ''} ${className}`}>
      {(title || subtitle) && (
        <div className={`card-body ${compact ? 'p-4' : ''}`}>
          {title && (
            typeof title === 'string' 
              ? <h2 className="card-title">{title}</h2>
              : title
          )}
          {subtitle && (
            typeof subtitle === 'string'
              ? <p className="text-sm opacity-70">{subtitle}</p>
              : subtitle
          )}
          <div className={compact ? 'mt-2' : 'mt-4'}>
            {children}
          </div>
          {footer && (
            <div className={`card-actions ${compact ? 'mt-2' : 'mt-4'}`}>
              {footer}
            </div>
          )}
        </div>
      )}
      {!title && !subtitle && (
        <div className={`card-body ${compact ? 'p-4' : ''}`}>
          {children}
          {footer && (
            <div className={`card-actions ${compact ? 'mt-2' : 'mt-4'}`}>
              {footer}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
