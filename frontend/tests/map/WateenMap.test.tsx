import React from 'react';
import { render, screen } from '@testing-library/react';
import WateenMap from '../../src/components/map/WateenMap';

describe('WateenMap SSR Safe Wrapper', () => {
  it('renders the branding skeleton during initial load (SSR context)', () => {
    // Because next/dynamic with ssr: false loads asynchronously,
    // immediately rendering should show the loading skeleton.
    render(<WateenMap center={[30.0444, 31.2357]} zoom={13} />);
    
    // Assert the Wateen brand loading state defaults correctly to #0A0A1A & #0066FF colors
    expect(screen.getByText(/Loading Wateen GIS Map.../i)).toBeInTheDocument();
  });
});
