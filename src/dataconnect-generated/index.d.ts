import { ConnectorConfig, DataConnect, QueryRef, QueryPromise, ExecuteQueryOptions, MutationRef, MutationPromise, DataConnectSettings } from 'firebase/data-connect';

export const connectorConfig: ConnectorConfig;
export const dataConnectSettings: DataConnectSettings;

export type TimestampString = string;
export type UUIDString = string;
export type Int64String = string;
export type DateString = string;




export interface Booking_Key {
  id: UUIDString;
  __typename?: 'Booking_Key';
}

export interface CreateBookingData {
  booking_insert: Booking_Key;
}

export interface CreateBookingVariables {
  guestId: UUIDString;
  hotelId: UUIDString;
  roomId: UUIDString;
  checkIn: DateString;
  checkOut: DateString;
  status: string;
}

export interface CreateGuestData {
  guest_insert: Guest_Key;
}

export interface CreateGuestVariables {
  fullName: string;
  email: string;
  phone: string;
}

export interface CreateHotelData {
  hotel_insert: Hotel_Key;
}

export interface CreateRoomData {
  room_insert: Room_Key;
}

export interface CreateRoomVariables {
  hotelId: UUIDString;
  roomNumber: string;
  type: string;
  status: string;
}

export interface CreateServiceRequestData {
  serviceRequest_insert: ServiceRequest_Key;
}

export interface CreateServiceRequestVariables {
  bookingId: UUIDString;
  desc: string;
  status: string;
}

export interface DeleteBookingData {
  booking_delete?: Booking_Key | null;
}

export interface DeleteBookingVariables {
  id: UUIDString;
}

export interface DeleteGuestData {
  guest_delete?: Guest_Key | null;
}

export interface DeleteGuestVariables {
  id: UUIDString;
}

export interface DeleteHotelData {
  hotel_delete?: Hotel_Key | null;
}

export interface DeleteHotelVariables {
  id: UUIDString;
}

export interface DeleteRoomData {
  room_delete?: Room_Key | null;
}

export interface DeleteRoomVariables {
  id: UUIDString;
}

export interface DeleteServiceRequestData {
  serviceRequest_delete?: ServiceRequest_Key | null;
}

export interface DeleteServiceRequestVariables {
  id: UUIDString;
}

export interface GetBookingData {
  booking?: {
    checkInDate: DateString;
    checkOutDate: DateString;
    status: string;
    totalAmountPaid?: number | null;
  };
}

export interface GetBookingVariables {
  id: UUIDString;
}

export interface GetGuestData {
  guest?: {
    fullName: string;
    email: string;
    phone: string;
  };
}

export interface GetGuestVariables {
  id: UUIDString;
}

export interface GetHotelData {
  hotel?: {
    name: string;
    location: string;
    currency: string;
  };
}

export interface GetHotelVariables {
  id: UUIDString;
}

export interface GetRoomData {
  room?: {
    roomNumber: string;
    type: string;
    status: string;
    pricePerNight?: number | null;
  };
}

export interface GetRoomVariables {
  id: UUIDString;
}

export interface GetServiceRequestData {
  serviceRequest?: {
    description: string;
    status: string;
    priority?: string | null;
  };
}

export interface GetServiceRequestVariables {
  id: UUIDString;
}

export interface Guest_Key {
  id: UUIDString;
  __typename?: 'Guest_Key';
}

export interface Hotel_Key {
  id: UUIDString;
  __typename?: 'Hotel_Key';
}

export interface ListGuestsData {
  guests: ({
    fullName: string;
    email: string;
  })[];
}

export interface ListHotelsData {
  hotels: ({
    name: string;
    location: string;
  })[];
}

export interface ListMyBookingsData {
  bookings: ({
    checkInDate: DateString;
    checkOutDate: DateString;
    status: string;
  })[];
}

export interface ListMyBookingsVariables {
  guestId: UUIDString;
}

export interface ListRoomsByHotelData {
  rooms: ({
    roomNumber: string;
    type: string;
  })[];
}

export interface ListRoomsByHotelVariables {
  hotelId: UUIDString;
}

export interface ListServiceRequestsByBookingData {
  serviceRequests: ({
    description: string;
    status: string;
  })[];
}

export interface ListServiceRequestsByBookingVariables {
  bookingId: UUIDString;
}

export interface Room_Key {
  id: UUIDString;
  __typename?: 'Room_Key';
}

export interface ServiceRequest_Key {
  id: UUIDString;
  __typename?: 'ServiceRequest_Key';
}

export interface UpdateBookingData {
  booking_update?: Booking_Key | null;
}

export interface UpdateBookingVariables {
  id: UUIDString;
  status?: string | null;
}

export interface UpdateGuestData {
  guest_update?: Guest_Key | null;
}

export interface UpdateGuestVariables {
  id: UUIDString;
  phone?: string | null;
}

export interface UpdateHotelData {
  hotel_update?: Hotel_Key | null;
}

export interface UpdateHotelVariables {
  id: UUIDString;
  name?: string | null;
}

export interface UpdateRoomData {
  room_update?: Room_Key | null;
}

export interface UpdateRoomVariables {
  id: UUIDString;
  status?: string | null;
}

export interface UpdateServiceRequestData {
  serviceRequest_update?: ServiceRequest_Key | null;
}

export interface UpdateServiceRequestVariables {
  id: UUIDString;
  status?: string | null;
}

interface CreateHotelRef {
  /* Allow users to create refs without passing in DataConnect */
  (): MutationRef<CreateHotelData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): MutationRef<CreateHotelData, undefined>;
  operationName: string;
}
export const createHotelRef: CreateHotelRef;

export function createHotel(): MutationPromise<CreateHotelData, undefined>;
export function createHotel(dc: DataConnect): MutationPromise<CreateHotelData, undefined>;

interface UpdateHotelRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateHotelVariables): MutationRef<UpdateHotelData, UpdateHotelVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: UpdateHotelVariables): MutationRef<UpdateHotelData, UpdateHotelVariables>;
  operationName: string;
}
export const updateHotelRef: UpdateHotelRef;

export function updateHotel(vars: UpdateHotelVariables): MutationPromise<UpdateHotelData, UpdateHotelVariables>;
export function updateHotel(dc: DataConnect, vars: UpdateHotelVariables): MutationPromise<UpdateHotelData, UpdateHotelVariables>;

interface DeleteHotelRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteHotelVariables): MutationRef<DeleteHotelData, DeleteHotelVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteHotelVariables): MutationRef<DeleteHotelData, DeleteHotelVariables>;
  operationName: string;
}
export const deleteHotelRef: DeleteHotelRef;

export function deleteHotel(vars: DeleteHotelVariables): MutationPromise<DeleteHotelData, DeleteHotelVariables>;
export function deleteHotel(dc: DataConnect, vars: DeleteHotelVariables): MutationPromise<DeleteHotelData, DeleteHotelVariables>;

interface GetHotelRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetHotelVariables): QueryRef<GetHotelData, GetHotelVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetHotelVariables): QueryRef<GetHotelData, GetHotelVariables>;
  operationName: string;
}
export const getHotelRef: GetHotelRef;

export function getHotel(vars: GetHotelVariables, options?: ExecuteQueryOptions): QueryPromise<GetHotelData, GetHotelVariables>;
export function getHotel(dc: DataConnect, vars: GetHotelVariables, options?: ExecuteQueryOptions): QueryPromise<GetHotelData, GetHotelVariables>;

interface ListHotelsRef {
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListHotelsData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): QueryRef<ListHotelsData, undefined>;
  operationName: string;
}
export const listHotelsRef: ListHotelsRef;

export function listHotels(options?: ExecuteQueryOptions): QueryPromise<ListHotelsData, undefined>;
export function listHotels(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListHotelsData, undefined>;

interface CreateRoomRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateRoomVariables): MutationRef<CreateRoomData, CreateRoomVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateRoomVariables): MutationRef<CreateRoomData, CreateRoomVariables>;
  operationName: string;
}
export const createRoomRef: CreateRoomRef;

export function createRoom(vars: CreateRoomVariables): MutationPromise<CreateRoomData, CreateRoomVariables>;
export function createRoom(dc: DataConnect, vars: CreateRoomVariables): MutationPromise<CreateRoomData, CreateRoomVariables>;

interface UpdateRoomRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateRoomVariables): MutationRef<UpdateRoomData, UpdateRoomVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: UpdateRoomVariables): MutationRef<UpdateRoomData, UpdateRoomVariables>;
  operationName: string;
}
export const updateRoomRef: UpdateRoomRef;

export function updateRoom(vars: UpdateRoomVariables): MutationPromise<UpdateRoomData, UpdateRoomVariables>;
export function updateRoom(dc: DataConnect, vars: UpdateRoomVariables): MutationPromise<UpdateRoomData, UpdateRoomVariables>;

interface DeleteRoomRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteRoomVariables): MutationRef<DeleteRoomData, DeleteRoomVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteRoomVariables): MutationRef<DeleteRoomData, DeleteRoomVariables>;
  operationName: string;
}
export const deleteRoomRef: DeleteRoomRef;

export function deleteRoom(vars: DeleteRoomVariables): MutationPromise<DeleteRoomData, DeleteRoomVariables>;
export function deleteRoom(dc: DataConnect, vars: DeleteRoomVariables): MutationPromise<DeleteRoomData, DeleteRoomVariables>;

interface GetRoomRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetRoomVariables): QueryRef<GetRoomData, GetRoomVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetRoomVariables): QueryRef<GetRoomData, GetRoomVariables>;
  operationName: string;
}
export const getRoomRef: GetRoomRef;

export function getRoom(vars: GetRoomVariables, options?: ExecuteQueryOptions): QueryPromise<GetRoomData, GetRoomVariables>;
export function getRoom(dc: DataConnect, vars: GetRoomVariables, options?: ExecuteQueryOptions): QueryPromise<GetRoomData, GetRoomVariables>;

interface ListRoomsByHotelRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListRoomsByHotelVariables): QueryRef<ListRoomsByHotelData, ListRoomsByHotelVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: ListRoomsByHotelVariables): QueryRef<ListRoomsByHotelData, ListRoomsByHotelVariables>;
  operationName: string;
}
export const listRoomsByHotelRef: ListRoomsByHotelRef;

export function listRoomsByHotel(vars: ListRoomsByHotelVariables, options?: ExecuteQueryOptions): QueryPromise<ListRoomsByHotelData, ListRoomsByHotelVariables>;
export function listRoomsByHotel(dc: DataConnect, vars: ListRoomsByHotelVariables, options?: ExecuteQueryOptions): QueryPromise<ListRoomsByHotelData, ListRoomsByHotelVariables>;

interface CreateGuestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateGuestVariables): MutationRef<CreateGuestData, CreateGuestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateGuestVariables): MutationRef<CreateGuestData, CreateGuestVariables>;
  operationName: string;
}
export const createGuestRef: CreateGuestRef;

export function createGuest(vars: CreateGuestVariables): MutationPromise<CreateGuestData, CreateGuestVariables>;
export function createGuest(dc: DataConnect, vars: CreateGuestVariables): MutationPromise<CreateGuestData, CreateGuestVariables>;

interface UpdateGuestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateGuestVariables): MutationRef<UpdateGuestData, UpdateGuestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: UpdateGuestVariables): MutationRef<UpdateGuestData, UpdateGuestVariables>;
  operationName: string;
}
export const updateGuestRef: UpdateGuestRef;

export function updateGuest(vars: UpdateGuestVariables): MutationPromise<UpdateGuestData, UpdateGuestVariables>;
export function updateGuest(dc: DataConnect, vars: UpdateGuestVariables): MutationPromise<UpdateGuestData, UpdateGuestVariables>;

interface DeleteGuestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteGuestVariables): MutationRef<DeleteGuestData, DeleteGuestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteGuestVariables): MutationRef<DeleteGuestData, DeleteGuestVariables>;
  operationName: string;
}
export const deleteGuestRef: DeleteGuestRef;

export function deleteGuest(vars: DeleteGuestVariables): MutationPromise<DeleteGuestData, DeleteGuestVariables>;
export function deleteGuest(dc: DataConnect, vars: DeleteGuestVariables): MutationPromise<DeleteGuestData, DeleteGuestVariables>;

interface GetGuestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetGuestVariables): QueryRef<GetGuestData, GetGuestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetGuestVariables): QueryRef<GetGuestData, GetGuestVariables>;
  operationName: string;
}
export const getGuestRef: GetGuestRef;

export function getGuest(vars: GetGuestVariables, options?: ExecuteQueryOptions): QueryPromise<GetGuestData, GetGuestVariables>;
export function getGuest(dc: DataConnect, vars: GetGuestVariables, options?: ExecuteQueryOptions): QueryPromise<GetGuestData, GetGuestVariables>;

interface ListGuestsRef {
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListGuestsData, undefined>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect): QueryRef<ListGuestsData, undefined>;
  operationName: string;
}
export const listGuestsRef: ListGuestsRef;

export function listGuests(options?: ExecuteQueryOptions): QueryPromise<ListGuestsData, undefined>;
export function listGuests(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListGuestsData, undefined>;

interface CreateBookingRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateBookingVariables): MutationRef<CreateBookingData, CreateBookingVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateBookingVariables): MutationRef<CreateBookingData, CreateBookingVariables>;
  operationName: string;
}
export const createBookingRef: CreateBookingRef;

export function createBooking(vars: CreateBookingVariables): MutationPromise<CreateBookingData, CreateBookingVariables>;
export function createBooking(dc: DataConnect, vars: CreateBookingVariables): MutationPromise<CreateBookingData, CreateBookingVariables>;

interface UpdateBookingRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateBookingVariables): MutationRef<UpdateBookingData, UpdateBookingVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: UpdateBookingVariables): MutationRef<UpdateBookingData, UpdateBookingVariables>;
  operationName: string;
}
export const updateBookingRef: UpdateBookingRef;

export function updateBooking(vars: UpdateBookingVariables): MutationPromise<UpdateBookingData, UpdateBookingVariables>;
export function updateBooking(dc: DataConnect, vars: UpdateBookingVariables): MutationPromise<UpdateBookingData, UpdateBookingVariables>;

interface DeleteBookingRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteBookingVariables): MutationRef<DeleteBookingData, DeleteBookingVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteBookingVariables): MutationRef<DeleteBookingData, DeleteBookingVariables>;
  operationName: string;
}
export const deleteBookingRef: DeleteBookingRef;

export function deleteBooking(vars: DeleteBookingVariables): MutationPromise<DeleteBookingData, DeleteBookingVariables>;
export function deleteBooking(dc: DataConnect, vars: DeleteBookingVariables): MutationPromise<DeleteBookingData, DeleteBookingVariables>;

interface GetBookingRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetBookingVariables): QueryRef<GetBookingData, GetBookingVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetBookingVariables): QueryRef<GetBookingData, GetBookingVariables>;
  operationName: string;
}
export const getBookingRef: GetBookingRef;

export function getBooking(vars: GetBookingVariables, options?: ExecuteQueryOptions): QueryPromise<GetBookingData, GetBookingVariables>;
export function getBooking(dc: DataConnect, vars: GetBookingVariables, options?: ExecuteQueryOptions): QueryPromise<GetBookingData, GetBookingVariables>;

interface ListMyBookingsRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListMyBookingsVariables): QueryRef<ListMyBookingsData, ListMyBookingsVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: ListMyBookingsVariables): QueryRef<ListMyBookingsData, ListMyBookingsVariables>;
  operationName: string;
}
export const listMyBookingsRef: ListMyBookingsRef;

export function listMyBookings(vars: ListMyBookingsVariables, options?: ExecuteQueryOptions): QueryPromise<ListMyBookingsData, ListMyBookingsVariables>;
export function listMyBookings(dc: DataConnect, vars: ListMyBookingsVariables, options?: ExecuteQueryOptions): QueryPromise<ListMyBookingsData, ListMyBookingsVariables>;

interface CreateServiceRequestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateServiceRequestVariables): MutationRef<CreateServiceRequestData, CreateServiceRequestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: CreateServiceRequestVariables): MutationRef<CreateServiceRequestData, CreateServiceRequestVariables>;
  operationName: string;
}
export const createServiceRequestRef: CreateServiceRequestRef;

export function createServiceRequest(vars: CreateServiceRequestVariables): MutationPromise<CreateServiceRequestData, CreateServiceRequestVariables>;
export function createServiceRequest(dc: DataConnect, vars: CreateServiceRequestVariables): MutationPromise<CreateServiceRequestData, CreateServiceRequestVariables>;

interface UpdateServiceRequestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateServiceRequestVariables): MutationRef<UpdateServiceRequestData, UpdateServiceRequestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: UpdateServiceRequestVariables): MutationRef<UpdateServiceRequestData, UpdateServiceRequestVariables>;
  operationName: string;
}
export const updateServiceRequestRef: UpdateServiceRequestRef;

export function updateServiceRequest(vars: UpdateServiceRequestVariables): MutationPromise<UpdateServiceRequestData, UpdateServiceRequestVariables>;
export function updateServiceRequest(dc: DataConnect, vars: UpdateServiceRequestVariables): MutationPromise<UpdateServiceRequestData, UpdateServiceRequestVariables>;

interface DeleteServiceRequestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteServiceRequestVariables): MutationRef<DeleteServiceRequestData, DeleteServiceRequestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: DeleteServiceRequestVariables): MutationRef<DeleteServiceRequestData, DeleteServiceRequestVariables>;
  operationName: string;
}
export const deleteServiceRequestRef: DeleteServiceRequestRef;

export function deleteServiceRequest(vars: DeleteServiceRequestVariables): MutationPromise<DeleteServiceRequestData, DeleteServiceRequestVariables>;
export function deleteServiceRequest(dc: DataConnect, vars: DeleteServiceRequestVariables): MutationPromise<DeleteServiceRequestData, DeleteServiceRequestVariables>;

interface GetServiceRequestRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetServiceRequestVariables): QueryRef<GetServiceRequestData, GetServiceRequestVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: GetServiceRequestVariables): QueryRef<GetServiceRequestData, GetServiceRequestVariables>;
  operationName: string;
}
export const getServiceRequestRef: GetServiceRequestRef;

export function getServiceRequest(vars: GetServiceRequestVariables, options?: ExecuteQueryOptions): QueryPromise<GetServiceRequestData, GetServiceRequestVariables>;
export function getServiceRequest(dc: DataConnect, vars: GetServiceRequestVariables, options?: ExecuteQueryOptions): QueryPromise<GetServiceRequestData, GetServiceRequestVariables>;

interface ListServiceRequestsByBookingRef {
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListServiceRequestsByBookingVariables): QueryRef<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;
  /* Allow users to pass in custom DataConnect instances */
  (dc: DataConnect, vars: ListServiceRequestsByBookingVariables): QueryRef<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;
  operationName: string;
}
export const listServiceRequestsByBookingRef: ListServiceRequestsByBookingRef;

export function listServiceRequestsByBooking(vars: ListServiceRequestsByBookingVariables, options?: ExecuteQueryOptions): QueryPromise<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;
export function listServiceRequestsByBooking(dc: DataConnect, vars: ListServiceRequestsByBookingVariables, options?: ExecuteQueryOptions): QueryPromise<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;

