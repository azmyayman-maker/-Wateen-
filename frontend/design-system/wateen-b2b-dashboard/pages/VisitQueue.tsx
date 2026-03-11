import React, { useState, useEffect } from 'react';
import { 
  List, 
  Datagrid, 
  TextField, 
  FunctionField, 
  useDataProvider, 
  useRefresh,
  useNotify,
  Button
} from 'react-admin';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Select, 
  MenuItem, 
  FormControl,
  InputLabel,
  CircularProgress,
  Chip
} from '@mui/material';

// Types
interface Visit {
  id: string;
  patient_district: string;
  service_type_name: string;
  urgency: string;
  final_price: string;
  remaining_seconds: number;
}

interface Nurse {
  user_id: string;
  first_name: string;
  last_name: string;
  specializations: string[];
}

// Sub-components

const CountdownTimer = ({ seconds }: { seconds: number }) => {
  const [timeLeft, setTimeLeft] = useState(seconds);

  useEffect(() => {
    if (timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timeLeft]);

  const mins = Math.floor(Math.max(0, timeLeft) / 60);
  const secs = Math.max(0, timeLeft) % 60;
  const formatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  let colorClass = 'countdown-green';
  let colorHex = '#22c55e'; // default green
  
  if (timeLeft <= 0) {
    return <span style={{ color: '#ef4444', fontWeight: 'bold' }}>منتهي</span>;
  } else if (timeLeft <= 60) {
    colorClass = 'countdown-red';
    colorHex = '#ef4444';
  } else if (timeLeft <= 120) {
    colorClass = 'countdown-yellow';
    colorHex = '#f59e0b';
  }

  return (
    <span 
      className={colorClass} 
      style={{ 
        color: colorHex, 
        fontWeight: 'bold',
        paddingInlineStart: 'var(--space-sm)'
      }}
      dir="rtl"
    >
      {formatted}
    </span>
  );
};

const UrgencyBadge = ({ urgency }: { urgency: string }) => {
  const config: Record<string, { label: string, color: string, pulse?: boolean }> = {
    'SOS': { label: 'طوارئ', color: '#ef4444', pulse: true }, // Red
    'CRITICAL': { label: 'حرجة', color: '#dc2626' }, // Dark Red
    'HIGH': { label: 'عالية', color: '#ea580c' }, // Orange
    'MEDIUM': { label: 'متوسطة', color: '#eab308' }, // Yellow
    'LOW': { label: 'منخفضة', color: '#22c55e' } // Green
  };

  const current = config[urgency] || config['LOW'];
  
  return (
    <Chip 
      label={current.label} 
      size="small"
      sx={{ 
        backgroundColor: current.color, 
        color: 'white',
        fontWeight: 'bold',
        animation: current.pulse ? 'pulse 2s infinite' : 'none',
        '@keyframes pulse': {
          '0%': { opacity: 1 },
          '50%': { opacity: 0.5 },
          '100%': { opacity: 1 }
        }
      }} 
    />
  );
};

const NurseAssignmentDialog = ({ 
  visitId, 
  open, 
  onClose,
  onSuccess
}: { 
  visitId: string, 
  open: boolean, 
  onClose: () => void,
  onSuccess: () => void
}) => {
  const [nurses, setNurses] = useState<Nurse[]>([]);
  const [selectedNurse, setSelectedNurse] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  
  const notify = useNotify();
  const dataProvider = useDataProvider();

  useEffect(() => {
    if (open) {
      setFetching(true);
      // We assume custom dataProvider method or directly fetch
      // For standard react-admin, we can use getList if adapted, but here we invoke dataProvider directly or use fetch
      fetch('/api/v1/visits/agency/available-nurses/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })
        .then(res => res.json())
        .then(data => {
          setNurses(data.results || []);
          setFetching(false);
        })
        .catch(err => {
          notify('خطأ في تحميل الممرضين', { type: 'error' });
          setFetching(false);
        });
    }
  }, [open, notify]);

  const handleAssign = async () => {
    if (!selectedNurse) return;
    
    setLoading(true);
    try {
      // In a real app we would get agency_id from auth context, here assuming it's available or handled by backend endpoint if we use a generic POST
      // Assuming generic /dispatch/manual/ endpoint per specs
      // Note: T034 says POST /api/v1/visits/agency/{agency_id}/dispatch/manual/
      const agencyId = localStorage.getItem('agency_id') || 'me';
      const response = await fetch(`/api/v1/visits/agency/${agencyId}/dispatch/manual/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          visit_id: visitId,
          nurse_id: selectedNurse
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        notify('تم تعيين الممرض/ة بنجاح', { type: 'success' });
        onSuccess();
        onClose();
      } else {
        notify(data.detail || 'حدث خطأ أثناء التعيين', { type: 'error' });
      }
    } catch (error) {
      notify('حدث خطأ غير متوقع', { type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} dir="rtl" maxWidth="sm" fullWidth>
      <DialogTitle sx={{ textAlign: 'start' }}>تعيين ممرض/ة للزيارة</DialogTitle>
      <DialogContent>
        {fetching ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
            <CircularProgress />
          </div>
        ) : (
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="nurse-select-label">اختر ممرض/ة</InputLabel>
            <Select
              labelId="nurse-select-label"
              value={selectedNurse}
              label="اختر ممرض/ة"
              onChange={(e) => setSelectedNurse(e.target.value)}
            >
              {nurses.map((nurse) => (
                <MenuItem key={nurse.user_id} value={nurse.user_id} dir="rtl">
                  {nurse.first_name} {nurse.last_name} {nurse.specializations?.length ? `(${nurse.specializations.join('، ')})` : ''}
                </MenuItem>
              ))}
              {nurses.length === 0 && (
                <MenuItem disabled value="">لا يوجد ممرضين متاحين حالياً</MenuItem>
              )}
            </Select>
          </FormControl>
        )}
      </DialogContent>
      <DialogActions sx={{ paddingInlineEnd: 'var(--space-lg)', paddingBottom: 'var(--space-lg)' }}>
        <Button onClick={onClose} label="إلغاء" disabled={loading} color="secondary" />
        <Button 
          onClick={handleAssign} 
          disabled={!selectedNurse || loading} 
          label={loading ? "جاري التعيين..." : "تأكيد التعيين"}
          variant="contained"
          sx={{ backgroundColor: 'var(--color-cta)' }}
        />
      </DialogActions>
    </Dialog>
  );
};

const AssignNurseButton = ({ visitId }: { visitId?: string }) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const refresh = useRefresh();

  if (!visitId) return null;

  return (
    <>
      <Button 
        onClick={(e) => { e.stopPropagation(); setDialogOpen(true); }}
        label="تعيين ممرض/ة"
        variant="outlined"
        sx={{ borderColor: 'var(--color-cta)', color: 'var(--color-cta)' }}
      />
      
      {dialogOpen && (
        <NurseAssignmentDialog
          visitId={visitId}
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          onSuccess={() => refresh()}
        />
      )}
    </>
  );
};

// Main exported component
export const VisitQueueList = () => {
  const refresh = useRefresh();

  // Auto-refresh every 30 seconds to sync countdown times with server
  useEffect(() => {
    const interval = setInterval(() => {
      refresh();
    }, 30000);
    return () => clearInterval(interval);
  }, [refresh]);

  return (
    <List 
      resource="visit-queue" 
      title="قائمة الزيارات المعلقة" 
      sort={{ field: 'urgency_order', order: 'ASC' }}
      sx={{ '& .RaList-main': { direction: 'rtl', textAlign: 'start' } }}
    >
      <Datagrid bulkActionButtons={false} rowClick={false}>
        <TextField source="patient_district" label="المنطقة" />
        <TextField source="service_type_name" label="نوع الخدمة" />
        <FunctionField 
          label="الأهمية" 
          render={(record: Visit) => <UrgencyBadge urgency={record.urgency} />} 
        />
        <TextField source="final_price" label="السعر (ج.م.)" />
        <FunctionField 
          label="الوقت المتبقي" 
          render={(record: Visit) => <CountdownTimer seconds={record.remaining_seconds} />} 
        />
        <FunctionField 
          label="إجراء" 
          render={(record: Visit) => <AssignNurseButton visitId={record.id} />} 
        />
      </Datagrid>
    </List>
  );
};

export default VisitQueueList;
