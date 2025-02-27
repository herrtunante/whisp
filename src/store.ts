import { create } from "zustand";
import { persist } from "zustand/middleware";

export type User = {
    id: string;
    email: string;
    name: string;
    apiToken: string;
    createdAt: string;
    lastLogin?: string;
};

type RecordData = {
    Geo_id: string;
    Area_ha: number;
    Country: string;
    EUFO_2020: number;
    GLAD_Primary: number;
    TMF_undist: number;
    JAXA_FNF_2020: number;
    GFC_TC_2020: number;
    GLAD_LULC__2020: number;
    ESRI_TC_2020: number;
    TMF_disturbed: number;
    RADD_alerts: string;
    TMF_plant: number;
    Oil_palm_Descals: number;
    Oil_palm_FDaP_: number;
    Cocoa_ETH: number;
    WDPA: string;
    OECM: string;
    KBA: string;
};

type AuthState = {
    user: User | null;
    isLoggedIn: boolean;
    jwtToken: string;
    login: (user: User, token: string) => void;
    logout: () => void;
};

type DataState = {
    token: string,
    data: RecordData[],
    geometryFile: File | null,
    geoIdsFile: File | null,
    error: string,
    geoIds: string[],
    isDisabled: boolean,
    selectedFile: string,
    geometry: string[],
    shpBase64: string,
    reset: () => void;
};

type StoreState = DataState & AuthState;

const initialDataState: Omit<DataState, 'reset'> = {
    token: "",
    data: [],
    geometryFile: null,
    geoIdsFile: null,
    error: "",
    geoIds: [""],
    isDisabled: true,
    selectedFile: "",
    geometry: [],
    shpBase64: ""
};

const initialAuthState: Omit<AuthState, 'login' | 'logout'> = {
    user: null,
    isLoggedIn: false,
    jwtToken: "",
};

export const useStore = create<StoreState>()(
    persist(
        (set) => ({
            ...initialDataState,
            ...initialAuthState,
            reset: () => set((state) => ({ 
                ...initialDataState, 
                user: state.user, 
                isLoggedIn: state.isLoggedIn,
                jwtToken: state.jwtToken
            })),
            login: (user, token) => set({ user, isLoggedIn: true, jwtToken: token }),
            logout: () => set({ user: null, isLoggedIn: false, jwtToken: "" }),
        }),
        {
            name: "whisp-storage",
            partialize: (state) => ({ 
                user: state.user, 
                isLoggedIn: state.isLoggedIn, 
                jwtToken: state.jwtToken 
            }),
        }
    )
);