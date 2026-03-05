/**
 * InvitationList Component
 * 
 * React Admin list view for managing nurse invitations.
 * Displays invitations with filtering, sorting, and RTL support.
 * 
 * Features:
 * - Status filtering (PENDING, ACCEPTED, EXPIRED, REVOKED)
 * - Phone number search
 * - Creation date sorting
 * - Revoke action for pending invitations
 * - Arabic RTL layout
 * 
 * B2B2C: Agency-scoped data - only shows invitations for the authenticated agency.
 */

import * as React from 'react';
import {
    List,
    Datagrid,
    TextField,
    DateField,
    ChipField,
    FunctionField,
    Filter,
    TextInput,
    SelectInput,
    TopToolbar,
    CreateButton,
    useListContext,
    useNotify,
    useRefresh,
    useTranslate,
} from 'react-admin';
import {
    Box,
    Typography,
    Button,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
} from '@mui/material';
import {
    Send as SendIcon,
    Cancel as CancelIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Block as BlockIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import { InvitationActions } from './InvitationActions';

// Typed record interface for NurseInvitation
interface InvitationRecord {
    id: string;
    phone: string;
    status: string;
    expires_at: string;
    created_at: string;
    token?: string;
}

// Status color mapping
const statusColors: Record<string, 'warning' | 'success' | 'error' | 'default'> = {
    PENDING: 'warning',
    ACCEPTED: 'success',
    EXPIRED: 'error',
    REVOKED: 'default',
};

// Status icon mapping
const statusIcons: Record<string, React.ReactElement> = {
    PENDING: <SendIcon fontSize="small" />,
    ACCEPTED: <CheckCircleIcon fontSize="small" />,
    EXPIRED: <ErrorIcon fontSize="small" />,
    REVOKED: <BlockIcon fontSize="small" />,
};

// Status label translation keys
const statusLabelKeys: Record<string, string> = {
    PENDING: 'قيد الانتظار',
    ACCEPTED: 'مقبول',
    EXPIRED: 'منتهي الصلاحية',
    REVOKED: 'ملغى',
};

// Invitation Filters Component
const InvitationFilters = () => {
    const translate = useTranslate();
    
    return (
        <Filter>
            <TextInput
                source="phone"
                label={translate('resources.invitations.fields.phone')}
                alwaysOn
                resettable
            />
            <SelectInput
                source="status"
                label={translate('resources.invitations.fields.status')}
                choices={[
                    { id: 'PENDING', name: statusLabelKeys.PENDING },
                    { id: 'ACCEPTED', name: statusLabelKeys.ACCEPTED },
                    { id: 'EXPIRED', name: statusLabelKeys.EXPIRED },
                    { id: 'REVOKED', name: statusLabelKeys.REVOKED },
                ]}
                alwaysOn
                resettable
            />
        </Filter>
    );
};

// List Actions Component
const InvitationListActions = () => (
    <TopToolbar>
        <CreateButton
            label="resources.invitations.actions.create"
            icon={<SendIcon />}
        />
    </TopToolbar>
);

// Status Chip Field
const StatusField = ({ record }: { record?: InvitationRecord }) => {
    if (!record) return null;
    
    const status = record.status as string;
    const color = statusColors[status] || 'default';
    const icon = statusIcons[status];
    const label = statusLabelKeys[status] || status;
    
    return (
        <Chip
            icon={icon}
            label={label}
            color={color}
            size="small"
            variant="outlined"
        />
    );
};

// Time Remaining Field
const TimeRemainingField = ({ record }: { record?: InvitationRecord }) => {
    if (!record || record.status !== 'PENDING') return null;
    
    const expiresAt = new Date(record.expires_at);
    const now = new Date();
    const diffMs = expiresAt.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffMs <= 0) {
        return (
            <Typography variant="body2" color="error">
                منتهي
            </Typography>
        );
    }
    
    if (diffHours < 24) {
        return (
            <Typography variant="body2" color={diffHours < 6 ? 'warning.main' : 'text.primary'}>
                {diffHours} ساعة {diffMinutes} دقيقة
            </Typography>
        );
    }
    
    const diffDays = Math.floor(diffHours / 24);
    return (
        <Typography variant="body2">
            {diffDays} يوم
        </Typography>
    );
};

// Main Invitation List Component
export const InvitationList = () => {
    const translate = useTranslate();
    
    return (
        <List
            filters={<InvitationFilters />}
            actions={<InvitationListActions />}
            sort={{ field: 'created_at', order: 'DESC' }}
            perPage={25}
            title={translate('resources.invitations.name')}
        >
            <Datagrid
                rowClick={false}
                bulkActionButtons={false}
                sx={{
                    '& .RaDatagrid-row': {
                        direction: 'rtl',
                    },
                }}
            >
                <TextField
                    source="phone"
                    label={translate('resources.invitations.fields.phone')}
                />
                <FunctionField
                    label={translate('resources.invitations.fields.status')}
                    render={(record: InvitationRecord) => <StatusField record={record} />}
                />
                <FunctionField
                    label={translate('resources.invitations.fields.time_remaining')}
                    render={(record: InvitationRecord) => <TimeRemainingField record={record} />}
                />
                <DateField
                    source="created_at"
                    label={translate('resources.invitations.fields.created_at')}
                    showTime
                    locales="ar-EG"
                />
                <DateField
                    source="expires_at"
                    label={translate('resources.invitations.fields.expires_at')}
                    showTime
                    locales="ar-EG"
                />
                <FunctionField
                    label={translate('resources.invitations.fields.actions')}
                    render={(_record: InvitationRecord) => (
                        <InvitationActions />
                    )}
                />
            </Datagrid>
        </List>
    );
};

export default InvitationList;