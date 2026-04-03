import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';
import toast from 'react-hot-toast';

// 1. Obține submissiile pentru un assignment
export function useSubmissions(assignmentId) {
  return useQuery({
    queryKey: ['submissions', assignmentId],
    queryFn: async () => {
      const { data } = await api.get(`/submissions/assignment/${assignmentId}`);
      return data;
    },
    enabled: !!assignmentId,
  });
}

// 2. Obține TOATE submissiile (pentru pagina globală)
export function useAllSubmissions() {
  return useQuery({
    queryKey: ['submissions', 'all'],
    queryFn: async () => {
      const { data } = await api.get(`/submissions/`);
      return data;
    }
  });
}

// 3. Încarcă o submisie nouă (Folosind FormData pentru FastAPI)
export function useUploadSubmission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ assignmentId, file }) => {
      const formData = new FormData();
      formData.append('assignment_id', assignmentId); // Trebuie sa coincida cu Form(...) din Python
      formData.append('file', file);
      
      const { data } = await api.post('/submissions/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
    onSuccess: (_, { assignmentId }) => {
      queryClient.invalidateQueries({ queryKey: ['submissions', assignmentId] });
      toast.success('Solution submitted successfully!');
    },
    onError: (err) => {
      toast.error(err.response?.data?.message || 'Failed to submit solution');
    }
  });
}

// 4. Editează (Înlocuiește) fișierul unei submisii
export function useUpdateSubmission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ subId, file }) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const { data } = await api.patch(`/submissions/${subId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data;
    },
    onSuccess: (_, { assignmentId }) => {
      queryClient.invalidateQueries({ queryKey: ['submissions', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['submissions', 'all'] });
      toast.success('Submission updated!');
    },
  });
}

// 5. Șterge o submisie
export function useDeleteSubmission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ subId }) => {
      await api.delete(`/submissions/${subId}`);
    },
    onSuccess: (_, { assignmentId }) => {
      queryClient.invalidateQueries({ queryKey: ['submissions', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['submissions', 'all'] });
      toast.success('Submission deleted!');
    },
  });
}

// 6. Funcție pentru descărcarea securizată a fișierului (cu Token)
export const downloadSubmissionFile = async (subId, filename) => {
  try {
    const response = await api.get(`/submissions/${subId}/file`, {
      responseType: 'blob', // Important pentru fișiere
    });
    
    // Creăm un URL local pentru fișier și forțăm descărcarea
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `submission_${subId}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    toast.error('Error downloading file');
  }
};