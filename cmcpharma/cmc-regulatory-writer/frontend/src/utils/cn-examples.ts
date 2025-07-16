// Example usage of the cn utility function

import { cn } from '../utils/cn';

// Basic usage - combining classes
const buttonClasses = cn(
  'px-4 py-2 rounded-md font-medium', // base classes
  'bg-blue-500 text-white',          // default state
  'hover:bg-blue-600',               // hover state
  'transition-colors duration-200'    // animation
);

// Conditional classes
const getButtonVariant = (variant: 'primary' | 'secondary', disabled: boolean) => {
  return cn(
    'px-4 py-2 rounded-md font-medium transition-colors duration-200', // base
    {
      'bg-blue-500 text-white hover:bg-blue-600': variant === 'primary' && !disabled,
      'bg-gray-200 text-gray-700 hover:bg-gray-300': variant === 'secondary' && !disabled,
      'bg-gray-100 text-gray-400 cursor-not-allowed': disabled,
    }
  );
};

// Merging conflicting Tailwind classes (tailwind-merge handles this)
const conflictingClasses = cn(
  'p-4',     // padding: 1rem
  'p-6',     // this will override p-4 (padding: 1.5rem)
  'text-sm', // font-size: 0.875rem
  'text-lg'  // this will override text-sm (font-size: 1.125rem)
);
// Result: 'p-6 text-lg' (conflicts resolved automatically)

export { buttonClasses, getButtonVariant, conflictingClasses };
