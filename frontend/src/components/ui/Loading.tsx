'use client';

interface LoadingProps {
  size?: 'xs' | 'sm' | 'md' | 'lg';
  text?: string;
  fullPage?: boolean;
}

export default function Loading({ 
  size = 'lg', 
  text = 'Loading...', 
  fullPage = false 
}: LoadingProps) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <span className={`loading loading-spinner loading-${size}`}></span>
      {text && <p className="text-center">{text}</p>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}
