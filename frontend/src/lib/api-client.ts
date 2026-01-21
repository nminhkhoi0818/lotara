const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiClient<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const fullUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`;
  const response = await fetch(fullUrl, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: "An error occurred" }));
    throw new ApiError(response.status, error.message || response.statusText);
  }

  return response.json();
}

// CRUD Operations
export const crud = {
  /**
   * GET request - Fetch data
   */
  get: async <T>(url: string, options?: RequestInit): Promise<T> => {
    return apiClient<T>(url, {
      ...options,
      method: "GET",
    });
  },

  /**
   * POST request - Create new resource
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  post: async <T, D = any>(
    url: string,
    data?: D,
    options?: RequestInit,
  ): Promise<T> => {
    return apiClient<T>(url, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PUT request - Update/replace resource
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  put: async <T, D = any>(
    url: string,
    data: D,
    options?: RequestInit,
  ): Promise<T> => {
    return apiClient<T>(url, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * PATCH request - Partial update
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  patch: async <T, D = any>(
    url: string,
    data: D,
    options?: RequestInit,
  ): Promise<T> => {
    return apiClient<T>(url, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  /**
   * DELETE request - Remove resource
   */
  delete: async <T = void>(url: string, options?: RequestInit): Promise<T> => {
    return apiClient<T>(url, {
      ...options,
      method: "DELETE",
    });
  },
};

// Export individual functions for convenience
export const { get, post, put, patch, delete: del } = crud;
