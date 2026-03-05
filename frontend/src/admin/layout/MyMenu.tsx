import { Menu } from "react-admin";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import MapIcon from "@mui/icons-material/Map";
import ListAltIcon from "@mui/icons-material/ListAlt";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import SettingsIcon from "@mui/icons-material/Settings";

export const MyMenu = () => {
    return (
        <Menu>
            <Menu.DashboardItem />
            <Menu.Item to="/nurses" primaryText="resources.nurses.name" leftIcon={<LocalHospitalIcon />} />
            <Menu.Item to="/coverage-area" primaryText="custom.menu.coverage_area" leftIcon={<MapIcon />} />
            <Menu.Item to="/visit-queue" primaryText="custom.menu.visit_queue" leftIcon={<ListAltIcon />} />
            <Menu.Item to="/financials" primaryText="custom.menu.financials" leftIcon={<AttachMoneyIcon />} />
            <Menu.Item to="/settings" primaryText="custom.menu.agency_settings" leftIcon={<SettingsIcon />} />
        </Menu>
    );
};
