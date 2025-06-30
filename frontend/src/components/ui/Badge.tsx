'use client';

import { ReactNode } from 'react';

type BadgeSize = 'xs' | 'sm' | 'md' | 'lg';
type BadgeVariant = 'default' | 'outline' | 'primary' | 'secondary' | 'accent' | 'ghost' | 'info' | 'success' | 'warning' | 'error';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
}

export default function Badge({ 
  children, 
  variant = 'default', 
  size = 'md',
  className = '' 
}: BadgeProps) {
  const variantClass = variant !== 'default' ? `badge-${variant}` : '';
  const sizeClass = size !== 'md' ? `badge-${size}` : '';
  
  return (
    <div className={`badge ${variantClass} ${sizeClass} ${className}`}>
      {children}
    </div>
  );
}
