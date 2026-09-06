import React from 'react';

interface GroundingBadgeProps {
  state?: 'verified' | 'unverified' | 'fallback' | 'stale' | 'partially_verified';
  isLive?: boolean;
  label?: string;
  size?: 'sm' | 'md';
}

export const GroundingBadge: React.FC<GroundingBadgeProps> = ({
  state = 'verified',
  isLive = true,
  label,
  size = 'md'
}) => {
  let badgeStyle = 'bg-emerald-50 text-emerald-800 border-emerald-300';
  let dotStyle = 'bg-emerald-600';
  let defaultLabel = '🟢 LIVE';

  if (!isLive || state === 'fallback' || state === 'stale') {
    badgeStyle = 'bg-amber-50 text-amber-800 border-amber-300';
    dotStyle = 'bg-amber-600';
    defaultLabel = '🟡 CACHED';
  } else if (state === 'unverified') {
    badgeStyle = 'bg-ochre-surface text-ochre-dark border-ochre-border';
    dotStyle = 'bg-ochre-alert';
    defaultLabel = '🔴 UNVERIFIED';
  } else if (state === 'partially_verified') {
    badgeStyle = 'bg-amber-50 text-amber-800 border-amber-300';
    dotStyle = 'bg-amber-600';
    defaultLabel = '🟡 PARTIAL';
  }

  const displayText = label || defaultLabel;
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border ${badgeStyle} ${padding} tracking-normal select-none`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotStyle}`} />
      <span>{displayText}</span>
    </span>
  );
};
