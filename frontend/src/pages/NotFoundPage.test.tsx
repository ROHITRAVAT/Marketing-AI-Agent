/// <reference types="@testing-library/jest-dom" />
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import NotFoundPage from './NotFoundPage';

describe('NotFoundPage', () => {
  it('renders a 404 message and a link to home', () => {
    render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>
    );
    
    // @ts-ignore
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    
    const linkElement = screen.getByRole('link', { name: /home/i });
    // @ts-ignore
    expect(linkElement).toBeInTheDocument();
    // @ts-ignore
    expect(linkElement).toHaveAttribute('href', '/');
  });
});
