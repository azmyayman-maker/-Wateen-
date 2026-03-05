/**
 * InvitationCreate Component
 * 
 * React Admin create view for sending nurse invitations.
 * 
 * Features:
 * - Phone number validation (Egyptian mobile format)
 * - Capacity check before sending
 * - Rate limit warning display
 * - Arabic RTL layout
 * 
 * B2B2C: Invitations are scoped to the authenticated agency.
 */

import * as React from 'react';
import {
    Create,
    SimpleForm,
    TextInput,
    useNotify,
    useRedirect,
    useTranslate,
    required,
} from 'react-admin';
import {
    Box,
    Typography,
    Alert,
    CircularProgress,
    Card,
    CardContent,
} from '@mui/material';
import {
    Send as SendIcon,
    Warning as WarningIcon,
} from '@mui/icons-material';

// API base URL — use env variable for staging/production
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Egyptian phone number validation regex
const EGYPTIAN_PHONE_REGEX = /^01[0-25][0-9]{8}$/;

// Phone number validator
const validatePhone = (value: string) => {
    if (!value) {
        return 'resources.invitations.validation.phone_required';
    }
    if (!EGYPTIAN_PHONE_REGEX.test(value)) {
        return 'resources.invitations.validation.phone_invalid';
    }
    return undefined;
};

// Capacity Warning Component
const CapacityWarning = ({ used, total }: { used: number; total: number }) => {
    const translate = useTranslate();
    
    if (total <= 0) return null;
    
    const percentage = Math.round((used / total) * 100);
    
    if (percentage < 80) {
        return null;
    }
    
    const remaining = total - used;
    
    return (
        <Alert
            severity={percentage >= 95 ? 'error' : 'warning'}
            icon={<WarningIcon />}
            sx={{ mb: 2 }}
        >
            <Typography variant="body2">
                {percentage >= 95
                    ? translate('resources.invitations.capacity_exhausted', {
                          remaining,
                          total,
                      })
                    : translate('resources.invitations.capacity_warning', {
                          remaining,
                          total,
                      })}
            </Typography>
        </Alert>
    );
};

// Rate Limit Warning Component
const RateLimitWarning = ({ remaining, resetTime }: { remaining: number; resetTime?: number }) => {
    const translate = useTranslate();
    
    if (remaining > 2) {
        return null;
    }
    
    return (
        <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
                {translate('resources.invitations.rate_limit_warning', {
                    remaining,
                    count: remaining,
                })}
            </Typography>
        </Alert>
    );
};

// Invitation Create Form
export const InvitationCreate = () => {
    const translate = useTranslate();
    const notify = useNotify();
    const redirect = useRedirect();
    const [capacityInfo, setCapacityInfo] = React.useState<{
        used: number;
        total: number;
    } | null>(null);
    const [rateLimitInfo, setRateLimitInfo] = React.useState<{
        remaining: number;
        resetTime?: number;
    } | null>(null);
    const [loading, setLoading] = React.useState(true);
    
    // Fetch capacity and rate limit info on mount
    React.useEffect(() => {
        const fetchInfo = async () => {
            try {
                // Fetch capacity info
                const capacityResponse = await fetch(
                    `${API_BASE}/agency/capacity/`,
                    { credentials: 'include' }
                );
                if (capacityResponse.ok) {
                    const data = await capacityResponse.json();
                    setCapacityInfo({
                        used: data.used || 0,
                        total: data.total || 0,
                    });
                }
                
                // Fetch rate limit info
                const rateLimitResponse = await fetch(
                    `${API_BASE}/agency/invitation-limits/`,
                    { credentials: 'include' }
                );
                if (rateLimitResponse.ok) {
                    const data = await rateLimitResponse.json();
                    setRateLimitInfo({
                        remaining: data.remaining || 6,
                        resetTime: data.reset_time,
                    });
                }
            } catch (error) {
                console.error('Failed to fetch info:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchInfo();
    }, []);
    
    const onSuccess = () => {
        notify(translate('resources.invitations.notifications.sent'), { type: 'success' });
        redirect('list', 'invitations');
    };
    
    const onError = (error: any) => {
        const message = error?.body?.detail || 'resources.invitations.notifications.error';
        notify(message, { type: 'error' });
    };
    
    return (
        <Create
            mutationOptions={{ onSuccess, onError }}
            title={translate('resources.invitations.create')}
        >
            <SimpleForm>
                {loading ? (
                    <Box display="flex" justifyContent="center" p={3}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        {/* Capacity Warning */}
                        {capacityInfo && (
                            <CapacityWarning
                                used={capacityInfo.used}
                                total={capacityInfo.total}
                            />
                        )}
                        
                        {/* Rate Limit Warning */}
                        {rateLimitInfo && (
                            <RateLimitWarning
                                remaining={rateLimitInfo.remaining}
                                resetTime={rateLimitInfo.resetTime}
                            />
                        )}
                        
                        {/* Info Card */}
                        <Card sx={{ mb: 3, bgcolor: 'background.default' }}>
                            <CardContent>
                                <Typography variant="body2" color="text.secondary">
                                    {translate('resources.invitations.help_text')}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                    {translate('resources.invitations.expiry_info')}
                                </Typography>
                            </CardContent>
                        </Card>
                        
                        {/* Phone Input */}
                        <TextInput
                            source="phone"
                            label={translate('resources.invitations.fields.phone')}
                            validate={[required(), validatePhone]}
                            fullWidth
                            helperText={translate('resources.invitations.phone_help')}
                            placeholder="01XXXXXXXXX"
                            inputProps={{
                                maxLength: 11,
                                dir: 'ltr',
                            }}
                        />
                    </>
                )}
            </SimpleForm>
        </Create>
    );
};

export default InvitationCreate;