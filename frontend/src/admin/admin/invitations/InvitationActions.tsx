/**
 * InvitationActions Component
 * 
 * Reusable action buttons for invitation management.
 * 
 * Features:
 * - Revoke invitation button with confirmation dialog
 * - Resend invitation button (for pending/expired)
 * - Copy invitation link button
 * - Arabic RTL support
 */

import * as React from 'react';
import { useNotify, useRefresh, useTranslate, useRecordContext } from 'react-admin';
import {
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    Snackbar,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    Cancel as CancelIcon,
    Refresh as RefreshIcon,
    Link as LinkIcon,
    ContentCopy as CopyIcon,
} from '@mui/icons-material';

// API base URL — use env variable for staging/production
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Status type
type InvitationStatus = 'PENDING' | 'ACCEPTED' | 'EXPIRED' | 'REVOKED';

// Props for RevokeInvitationButton
interface RevokeInvitationButtonProps {
    onRevoked?: () => void;
}

/**
 * Revoke Invitation Button
 * 
 * Shows a confirmation dialog before revoking a pending invitation.
 */
export const RevokeInvitationButton: React.FC<RevokeInvitationButtonProps> = ({ onRevoked }) => {
    const [open, setOpen] = React.useState(false);
    const [loading, setLoading] = React.useState(false);
    const notify = useNotify();
    const translate = useTranslate();
    const record = useRecordContext();
    
    if (!record || record.status !== 'PENDING') {
        return null;
    }
    
    const handleRevoke = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${API_BASE}/agency/invitations/${record.id}/revoke/`,
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to revoke invitation');
            }
            
            notify(translate('resources.invitations.notifications.revoked'), { type: 'success' });
            onRevoked?.();
        } catch (error: any) {
            notify(
                error.message || translate('resources.invitations.notifications.revoke_error'),
                { type: 'error' }
            );
        } finally {
            setLoading(false);
            setOpen(false);
        }
    };
    
    return (
        <>
            <Button
                size="small"
                color="error"
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={(e) => {
                    e.stopPropagation();
                    setOpen(true);
                }}
            >
                {translate('resources.invitations.actions.revoke')}
            </Button>
            
            <Dialog open={open} onClose={() => setOpen(false)}>
                <DialogTitle>
                    {translate('resources.invitations.confirm_revoke.title')}
                </DialogTitle>
                <DialogContent>
                    <Alert severity="warning">
                        {translate('resources.invitations.confirm_revoke.message', {
                            phone: record.phone,
                        })}
                    </Alert>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>
                        {translate('ra.action.cancel')}
                    </Button>
                    <Button
                        variant="contained"
                        color="error"
                        onClick={handleRevoke}
                        disabled={loading}
                    >
                        {translate('resources.invitations.actions.revoke_confirm')}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

/**
 * Resend Invitation Button
 * 
 * Allows resending an expired invitation.
 */
export const ResendInvitationButton: React.FC = () => {
    const [loading, setLoading] = React.useState(false);
    const notify = useNotify();
    const refresh = useRefresh();
    const translate = useTranslate();
    const record = useRecordContext();
    
    if (!record || record.status !== 'EXPIRED') {
        return null;
    }
    
    const handleResend = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${API_BASE}/agency/invitations/`,
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ phone: record.phone }),
                }
            );
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to resend invitation');
            }
            
            notify(translate('resources.invitations.notifications.resent'), { type: 'success' });
            refresh();
        } catch (error: any) {
            notify(
                error.message || translate('resources.invitations.notifications.error'),
                { type: 'error' }
            );
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <Button
            size="small"
            color="primary"
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleResend}
            disabled={loading}
        >
            {translate('resources.invitations.actions.resend')}
        </Button>
    );
};

/**
 * Copy Invitation Link Button
 * 
 * Copies the invitation link to clipboard.
 */
export const CopyInvitationLinkButton: React.FC = () => {
    const [copied, setCopied] = React.useState(false);
    const translate = useTranslate();
    const notify = useNotify();
    const record = useRecordContext();
    
    if (!record || !record.token) {
        return null;
    }
    
    const invitationUrl = `${window.location.origin}/accept-invitation?token=${record.token}`;
    
    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(invitationUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // Clipboard API may fail in non-HTTPS contexts
            notify(translate('resources.invitations.notifications.error'), { type: 'error' });
        }
    };
    
    return (
        <Tooltip title={translate('resources.invitations.actions.copy_link')}>
            <IconButton size="small" onClick={handleCopy}>
                {copied ? <LinkIcon /> : <CopyIcon />}
            </IconButton>
        </Tooltip>
    );
};

/**
 * Combined Invitation Actions Component
 * 
 * Shows all applicable actions for an invitation.
 */
export const InvitationActions: React.FC = () => {
    const record = useRecordContext();
    const refresh = useRefresh();
    
    if (!record) {
        return null;
    }
    
    return (
        <>
            <RevokeInvitationButton onRevoked={refresh} />
            <ResendInvitationButton />
        </>
    );
};

export default InvitationActions;