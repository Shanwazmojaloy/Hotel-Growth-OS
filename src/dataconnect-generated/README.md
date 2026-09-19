# Generated TypeScript README
This README will guide you through the process of using the generated JavaScript SDK package for the connector `example`. It will also provide examples on how to use your generated SDK to call your Data Connect queries and mutations.

***NOTE:** This README is generated alongside the generated SDK. If you make changes to this file, they will be overwritten when the SDK is regenerated.*

# Table of Contents
- [**Overview**](#generated-javascript-readme)
- [**Accessing the connector**](#accessing-the-connector)
  - [*Connecting to the local Emulator*](#connecting-to-the-local-emulator)
- [**Queries**](#queries)
  - [*GetHotel*](#gethotel)
  - [*ListHotels*](#listhotels)
  - [*GetRoom*](#getroom)
  - [*ListRoomsByHotel*](#listroomsbyhotel)
  - [*GetGuest*](#getguest)
  - [*ListGuests*](#listguests)
  - [*GetBooking*](#getbooking)
  - [*ListMyBookings*](#listmybookings)
  - [*GetServiceRequest*](#getservicerequest)
  - [*ListServiceRequestsByBooking*](#listservicerequestsbybooking)
- [**Mutations**](#mutations)
  - [*CreateHotel*](#createhotel)
  - [*UpdateHotel*](#updatehotel)
  - [*DeleteHotel*](#deletehotel)
  - [*CreateRoom*](#createroom)
  - [*UpdateRoom*](#updateroom)
  - [*DeleteRoom*](#deleteroom)
  - [*CreateGuest*](#createguest)
  - [*UpdateGuest*](#updateguest)
  - [*DeleteGuest*](#deleteguest)
  - [*CreateBooking*](#createbooking)
  - [*UpdateBooking*](#updatebooking)
  - [*DeleteBooking*](#deletebooking)
  - [*CreateServiceRequest*](#createservicerequest)
  - [*UpdateServiceRequest*](#updateservicerequest)
  - [*DeleteServiceRequest*](#deleteservicerequest)

# Accessing the connector
A connector is a collection of Queries and Mutations. One SDK is generated for each connector - this SDK is generated for the connector `example`. You can find more information about connectors in the [Data Connect documentation](https://firebase.google.com/docs/data-connect#how-does).

You can use this generated SDK by importing from the package `@dataconnect/generated` as shown below. Both CommonJS and ESM imports are supported.

You can also follow the instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#set-client).

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
```

## Connecting to the local Emulator
By default, the connector will connect to the production service.

To connect to the emulator, you can use the following code.
You can also follow the emulator instructions from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#instrument-clients).

```typescript
import { connectDataConnectEmulator, getDataConnect } from 'firebase/data-connect';
import { connectorConfig } from '@dataconnect/generated';

const dataConnect = getDataConnect(connectorConfig);
connectDataConnectEmulator(dataConnect, 'localhost', 9399);
```

After it's initialized, you can call your Data Connect [queries](#queries) and [mutations](#mutations) from your generated SDK.

# Queries

There are two ways to execute a Data Connect Query using the generated Web SDK:
- Using a Query Reference function, which returns a `QueryRef`
  - The `QueryRef` can be used as an argument to `executeQuery()`, which will execute the Query and return a `QueryPromise`
- Using an action shortcut function, which returns a `QueryPromise`
  - Calling the action shortcut function will execute the Query and return a `QueryPromise`

The following is true for both the action shortcut function and the `QueryRef` function:
- The `QueryPromise` returned will resolve to the result of the Query once it has finished executing
- If the Query accepts arguments, both the action shortcut function and the `QueryRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Query
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each query. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-queries).

## GetHotel
You can execute the `GetHotel` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getHotel(vars: GetHotelVariables, options?: ExecuteQueryOptions): QueryPromise<GetHotelData, GetHotelVariables>;

interface GetHotelRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetHotelVariables): QueryRef<GetHotelData, GetHotelVariables>;
}
export const getHotelRef: GetHotelRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getHotel(dc: DataConnect, vars: GetHotelVariables, options?: ExecuteQueryOptions): QueryPromise<GetHotelData, GetHotelVariables>;

interface GetHotelRef {
  ...
  (dc: DataConnect, vars: GetHotelVariables): QueryRef<GetHotelData, GetHotelVariables>;
}
export const getHotelRef: GetHotelRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getHotelRef:
```typescript
const name = getHotelRef.operationName;
console.log(name);
```

### Variables
The `GetHotel` query requires an argument of type `GetHotelVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetHotelVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `GetHotel` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetHotelData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetHotelData {
  hotel?: {
    name: string;
    location: string;
    currency: string;
  };
}
```
### Using `GetHotel`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getHotel, GetHotelVariables } from '@dataconnect/generated';

// The `GetHotel` query requires an argument of type `GetHotelVariables`:
const getHotelVars: GetHotelVariables = {
  id: ..., 
};

// Call the `getHotel()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getHotel(getHotelVars);
// Variables can be defined inline as well.
const { data } = await getHotel({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getHotel(dataConnect, getHotelVars);

console.log(data.hotel);

// Or, you can use the `Promise` API.
getHotel(getHotelVars).then((response) => {
  const data = response.data;
  console.log(data.hotel);
});
```

### Using `GetHotel`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getHotelRef, GetHotelVariables } from '@dataconnect/generated';

// The `GetHotel` query requires an argument of type `GetHotelVariables`:
const getHotelVars: GetHotelVariables = {
  id: ..., 
};

// Call the `getHotelRef()` function to get a reference to the query.
const ref = getHotelRef(getHotelVars);
// Variables can be defined inline as well.
const ref = getHotelRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getHotelRef(dataConnect, getHotelVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.hotel);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.hotel);
});
```

## ListHotels
You can execute the `ListHotels` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listHotels(options?: ExecuteQueryOptions): QueryPromise<ListHotelsData, undefined>;

interface ListHotelsRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListHotelsData, undefined>;
}
export const listHotelsRef: ListHotelsRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listHotels(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListHotelsData, undefined>;

interface ListHotelsRef {
  ...
  (dc: DataConnect): QueryRef<ListHotelsData, undefined>;
}
export const listHotelsRef: ListHotelsRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listHotelsRef:
```typescript
const name = listHotelsRef.operationName;
console.log(name);
```

### Variables
The `ListHotels` query has no variables.
### Return Type
Recall that executing the `ListHotels` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListHotelsData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListHotelsData {
  hotels: ({
    name: string;
    location: string;
  })[];
}
```
### Using `ListHotels`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listHotels } from '@dataconnect/generated';


// Call the `listHotels()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listHotels();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listHotels(dataConnect);

console.log(data.hotels);

// Or, you can use the `Promise` API.
listHotels().then((response) => {
  const data = response.data;
  console.log(data.hotels);
});
```

### Using `ListHotels`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listHotelsRef } from '@dataconnect/generated';


// Call the `listHotelsRef()` function to get a reference to the query.
const ref = listHotelsRef();

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listHotelsRef(dataConnect);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.hotels);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.hotels);
});
```

## GetRoom
You can execute the `GetRoom` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getRoom(vars: GetRoomVariables, options?: ExecuteQueryOptions): QueryPromise<GetRoomData, GetRoomVariables>;

interface GetRoomRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetRoomVariables): QueryRef<GetRoomData, GetRoomVariables>;
}
export const getRoomRef: GetRoomRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getRoom(dc: DataConnect, vars: GetRoomVariables, options?: ExecuteQueryOptions): QueryPromise<GetRoomData, GetRoomVariables>;

interface GetRoomRef {
  ...
  (dc: DataConnect, vars: GetRoomVariables): QueryRef<GetRoomData, GetRoomVariables>;
}
export const getRoomRef: GetRoomRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getRoomRef:
```typescript
const name = getRoomRef.operationName;
console.log(name);
```

### Variables
The `GetRoom` query requires an argument of type `GetRoomVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetRoomVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `GetRoom` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetRoomData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetRoomData {
  room?: {
    roomNumber: string;
    type: string;
    status: string;
    pricePerNight?: number | null;
  };
}
```
### Using `GetRoom`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getRoom, GetRoomVariables } from '@dataconnect/generated';

// The `GetRoom` query requires an argument of type `GetRoomVariables`:
const getRoomVars: GetRoomVariables = {
  id: ..., 
};

// Call the `getRoom()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getRoom(getRoomVars);
// Variables can be defined inline as well.
const { data } = await getRoom({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getRoom(dataConnect, getRoomVars);

console.log(data.room);

// Or, you can use the `Promise` API.
getRoom(getRoomVars).then((response) => {
  const data = response.data;
  console.log(data.room);
});
```

### Using `GetRoom`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getRoomRef, GetRoomVariables } from '@dataconnect/generated';

// The `GetRoom` query requires an argument of type `GetRoomVariables`:
const getRoomVars: GetRoomVariables = {
  id: ..., 
};

// Call the `getRoomRef()` function to get a reference to the query.
const ref = getRoomRef(getRoomVars);
// Variables can be defined inline as well.
const ref = getRoomRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getRoomRef(dataConnect, getRoomVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.room);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.room);
});
```

## ListRoomsByHotel
You can execute the `ListRoomsByHotel` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listRoomsByHotel(vars: ListRoomsByHotelVariables, options?: ExecuteQueryOptions): QueryPromise<ListRoomsByHotelData, ListRoomsByHotelVariables>;

interface ListRoomsByHotelRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListRoomsByHotelVariables): QueryRef<ListRoomsByHotelData, ListRoomsByHotelVariables>;
}
export const listRoomsByHotelRef: ListRoomsByHotelRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listRoomsByHotel(dc: DataConnect, vars: ListRoomsByHotelVariables, options?: ExecuteQueryOptions): QueryPromise<ListRoomsByHotelData, ListRoomsByHotelVariables>;

interface ListRoomsByHotelRef {
  ...
  (dc: DataConnect, vars: ListRoomsByHotelVariables): QueryRef<ListRoomsByHotelData, ListRoomsByHotelVariables>;
}
export const listRoomsByHotelRef: ListRoomsByHotelRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listRoomsByHotelRef:
```typescript
const name = listRoomsByHotelRef.operationName;
console.log(name);
```

### Variables
The `ListRoomsByHotel` query requires an argument of type `ListRoomsByHotelVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface ListRoomsByHotelVariables {
  hotelId: UUIDString;
}
```
### Return Type
Recall that executing the `ListRoomsByHotel` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListRoomsByHotelData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListRoomsByHotelData {
  rooms: ({
    roomNumber: string;
    type: string;
  })[];
}
```
### Using `ListRoomsByHotel`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listRoomsByHotel, ListRoomsByHotelVariables } from '@dataconnect/generated';

// The `ListRoomsByHotel` query requires an argument of type `ListRoomsByHotelVariables`:
const listRoomsByHotelVars: ListRoomsByHotelVariables = {
  hotelId: ..., 
};

// Call the `listRoomsByHotel()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listRoomsByHotel(listRoomsByHotelVars);
// Variables can be defined inline as well.
const { data } = await listRoomsByHotel({ hotelId: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listRoomsByHotel(dataConnect, listRoomsByHotelVars);

console.log(data.rooms);

// Or, you can use the `Promise` API.
listRoomsByHotel(listRoomsByHotelVars).then((response) => {
  const data = response.data;
  console.log(data.rooms);
});
```

### Using `ListRoomsByHotel`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listRoomsByHotelRef, ListRoomsByHotelVariables } from '@dataconnect/generated';

// The `ListRoomsByHotel` query requires an argument of type `ListRoomsByHotelVariables`:
const listRoomsByHotelVars: ListRoomsByHotelVariables = {
  hotelId: ..., 
};

// Call the `listRoomsByHotelRef()` function to get a reference to the query.
const ref = listRoomsByHotelRef(listRoomsByHotelVars);
// Variables can be defined inline as well.
const ref = listRoomsByHotelRef({ hotelId: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listRoomsByHotelRef(dataConnect, listRoomsByHotelVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.rooms);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.rooms);
});
```

## GetGuest
You can execute the `GetGuest` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getGuest(vars: GetGuestVariables, options?: ExecuteQueryOptions): QueryPromise<GetGuestData, GetGuestVariables>;

interface GetGuestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetGuestVariables): QueryRef<GetGuestData, GetGuestVariables>;
}
export const getGuestRef: GetGuestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getGuest(dc: DataConnect, vars: GetGuestVariables, options?: ExecuteQueryOptions): QueryPromise<GetGuestData, GetGuestVariables>;

interface GetGuestRef {
  ...
  (dc: DataConnect, vars: GetGuestVariables): QueryRef<GetGuestData, GetGuestVariables>;
}
export const getGuestRef: GetGuestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getGuestRef:
```typescript
const name = getGuestRef.operationName;
console.log(name);
```

### Variables
The `GetGuest` query requires an argument of type `GetGuestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetGuestVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `GetGuest` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetGuestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetGuestData {
  guest?: {
    fullName: string;
    email: string;
    phone: string;
  };
}
```
### Using `GetGuest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getGuest, GetGuestVariables } from '@dataconnect/generated';

// The `GetGuest` query requires an argument of type `GetGuestVariables`:
const getGuestVars: GetGuestVariables = {
  id: ..., 
};

// Call the `getGuest()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getGuest(getGuestVars);
// Variables can be defined inline as well.
const { data } = await getGuest({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getGuest(dataConnect, getGuestVars);

console.log(data.guest);

// Or, you can use the `Promise` API.
getGuest(getGuestVars).then((response) => {
  const data = response.data;
  console.log(data.guest);
});
```

### Using `GetGuest`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getGuestRef, GetGuestVariables } from '@dataconnect/generated';

// The `GetGuest` query requires an argument of type `GetGuestVariables`:
const getGuestVars: GetGuestVariables = {
  id: ..., 
};

// Call the `getGuestRef()` function to get a reference to the query.
const ref = getGuestRef(getGuestVars);
// Variables can be defined inline as well.
const ref = getGuestRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getGuestRef(dataConnect, getGuestVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.guest);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.guest);
});
```

## ListGuests
You can execute the `ListGuests` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listGuests(options?: ExecuteQueryOptions): QueryPromise<ListGuestsData, undefined>;

interface ListGuestsRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): QueryRef<ListGuestsData, undefined>;
}
export const listGuestsRef: ListGuestsRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listGuests(dc: DataConnect, options?: ExecuteQueryOptions): QueryPromise<ListGuestsData, undefined>;

interface ListGuestsRef {
  ...
  (dc: DataConnect): QueryRef<ListGuestsData, undefined>;
}
export const listGuestsRef: ListGuestsRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listGuestsRef:
```typescript
const name = listGuestsRef.operationName;
console.log(name);
```

### Variables
The `ListGuests` query has no variables.
### Return Type
Recall that executing the `ListGuests` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListGuestsData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListGuestsData {
  guests: ({
    fullName: string;
    email: string;
  })[];
}
```
### Using `ListGuests`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listGuests } from '@dataconnect/generated';


// Call the `listGuests()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listGuests();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listGuests(dataConnect);

console.log(data.guests);

// Or, you can use the `Promise` API.
listGuests().then((response) => {
  const data = response.data;
  console.log(data.guests);
});
```

### Using `ListGuests`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listGuestsRef } from '@dataconnect/generated';


// Call the `listGuestsRef()` function to get a reference to the query.
const ref = listGuestsRef();

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listGuestsRef(dataConnect);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.guests);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.guests);
});
```

## GetBooking
You can execute the `GetBooking` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getBooking(vars: GetBookingVariables, options?: ExecuteQueryOptions): QueryPromise<GetBookingData, GetBookingVariables>;

interface GetBookingRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetBookingVariables): QueryRef<GetBookingData, GetBookingVariables>;
}
export const getBookingRef: GetBookingRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getBooking(dc: DataConnect, vars: GetBookingVariables, options?: ExecuteQueryOptions): QueryPromise<GetBookingData, GetBookingVariables>;

interface GetBookingRef {
  ...
  (dc: DataConnect, vars: GetBookingVariables): QueryRef<GetBookingData, GetBookingVariables>;
}
export const getBookingRef: GetBookingRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getBookingRef:
```typescript
const name = getBookingRef.operationName;
console.log(name);
```

### Variables
The `GetBooking` query requires an argument of type `GetBookingVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetBookingVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `GetBooking` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetBookingData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetBookingData {
  booking?: {
    checkInDate: DateString;
    checkOutDate: DateString;
    status: string;
    totalAmountPaid?: number | null;
  };
}
```
### Using `GetBooking`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getBooking, GetBookingVariables } from '@dataconnect/generated';

// The `GetBooking` query requires an argument of type `GetBookingVariables`:
const getBookingVars: GetBookingVariables = {
  id: ..., 
};

// Call the `getBooking()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getBooking(getBookingVars);
// Variables can be defined inline as well.
const { data } = await getBooking({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getBooking(dataConnect, getBookingVars);

console.log(data.booking);

// Or, you can use the `Promise` API.
getBooking(getBookingVars).then((response) => {
  const data = response.data;
  console.log(data.booking);
});
```

### Using `GetBooking`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getBookingRef, GetBookingVariables } from '@dataconnect/generated';

// The `GetBooking` query requires an argument of type `GetBookingVariables`:
const getBookingVars: GetBookingVariables = {
  id: ..., 
};

// Call the `getBookingRef()` function to get a reference to the query.
const ref = getBookingRef(getBookingVars);
// Variables can be defined inline as well.
const ref = getBookingRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getBookingRef(dataConnect, getBookingVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.booking);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.booking);
});
```

## ListMyBookings
You can execute the `ListMyBookings` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listMyBookings(vars: ListMyBookingsVariables, options?: ExecuteQueryOptions): QueryPromise<ListMyBookingsData, ListMyBookingsVariables>;

interface ListMyBookingsRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListMyBookingsVariables): QueryRef<ListMyBookingsData, ListMyBookingsVariables>;
}
export const listMyBookingsRef: ListMyBookingsRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listMyBookings(dc: DataConnect, vars: ListMyBookingsVariables, options?: ExecuteQueryOptions): QueryPromise<ListMyBookingsData, ListMyBookingsVariables>;

interface ListMyBookingsRef {
  ...
  (dc: DataConnect, vars: ListMyBookingsVariables): QueryRef<ListMyBookingsData, ListMyBookingsVariables>;
}
export const listMyBookingsRef: ListMyBookingsRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listMyBookingsRef:
```typescript
const name = listMyBookingsRef.operationName;
console.log(name);
```

### Variables
The `ListMyBookings` query requires an argument of type `ListMyBookingsVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface ListMyBookingsVariables {
  guestId: UUIDString;
}
```
### Return Type
Recall that executing the `ListMyBookings` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListMyBookingsData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListMyBookingsData {
  bookings: ({
    checkInDate: DateString;
    checkOutDate: DateString;
    status: string;
  })[];
}
```
### Using `ListMyBookings`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listMyBookings, ListMyBookingsVariables } from '@dataconnect/generated';

// The `ListMyBookings` query requires an argument of type `ListMyBookingsVariables`:
const listMyBookingsVars: ListMyBookingsVariables = {
  guestId: ..., 
};

// Call the `listMyBookings()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listMyBookings(listMyBookingsVars);
// Variables can be defined inline as well.
const { data } = await listMyBookings({ guestId: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listMyBookings(dataConnect, listMyBookingsVars);

console.log(data.bookings);

// Or, you can use the `Promise` API.
listMyBookings(listMyBookingsVars).then((response) => {
  const data = response.data;
  console.log(data.bookings);
});
```

### Using `ListMyBookings`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listMyBookingsRef, ListMyBookingsVariables } from '@dataconnect/generated';

// The `ListMyBookings` query requires an argument of type `ListMyBookingsVariables`:
const listMyBookingsVars: ListMyBookingsVariables = {
  guestId: ..., 
};

// Call the `listMyBookingsRef()` function to get a reference to the query.
const ref = listMyBookingsRef(listMyBookingsVars);
// Variables can be defined inline as well.
const ref = listMyBookingsRef({ guestId: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listMyBookingsRef(dataConnect, listMyBookingsVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.bookings);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.bookings);
});
```

## GetServiceRequest
You can execute the `GetServiceRequest` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
getServiceRequest(vars: GetServiceRequestVariables, options?: ExecuteQueryOptions): QueryPromise<GetServiceRequestData, GetServiceRequestVariables>;

interface GetServiceRequestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: GetServiceRequestVariables): QueryRef<GetServiceRequestData, GetServiceRequestVariables>;
}
export const getServiceRequestRef: GetServiceRequestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
getServiceRequest(dc: DataConnect, vars: GetServiceRequestVariables, options?: ExecuteQueryOptions): QueryPromise<GetServiceRequestData, GetServiceRequestVariables>;

interface GetServiceRequestRef {
  ...
  (dc: DataConnect, vars: GetServiceRequestVariables): QueryRef<GetServiceRequestData, GetServiceRequestVariables>;
}
export const getServiceRequestRef: GetServiceRequestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the getServiceRequestRef:
```typescript
const name = getServiceRequestRef.operationName;
console.log(name);
```

### Variables
The `GetServiceRequest` query requires an argument of type `GetServiceRequestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface GetServiceRequestVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `GetServiceRequest` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `GetServiceRequestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface GetServiceRequestData {
  serviceRequest?: {
    description: string;
    status: string;
    priority?: string | null;
  };
}
```
### Using `GetServiceRequest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, getServiceRequest, GetServiceRequestVariables } from '@dataconnect/generated';

// The `GetServiceRequest` query requires an argument of type `GetServiceRequestVariables`:
const getServiceRequestVars: GetServiceRequestVariables = {
  id: ..., 
};

// Call the `getServiceRequest()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await getServiceRequest(getServiceRequestVars);
// Variables can be defined inline as well.
const { data } = await getServiceRequest({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await getServiceRequest(dataConnect, getServiceRequestVars);

console.log(data.serviceRequest);

// Or, you can use the `Promise` API.
getServiceRequest(getServiceRequestVars).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest);
});
```

### Using `GetServiceRequest`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, getServiceRequestRef, GetServiceRequestVariables } from '@dataconnect/generated';

// The `GetServiceRequest` query requires an argument of type `GetServiceRequestVariables`:
const getServiceRequestVars: GetServiceRequestVariables = {
  id: ..., 
};

// Call the `getServiceRequestRef()` function to get a reference to the query.
const ref = getServiceRequestRef(getServiceRequestVars);
// Variables can be defined inline as well.
const ref = getServiceRequestRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = getServiceRequestRef(dataConnect, getServiceRequestVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.serviceRequest);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest);
});
```

## ListServiceRequestsByBooking
You can execute the `ListServiceRequestsByBooking` query using the following action shortcut function, or by calling `executeQuery()` after calling the following `QueryRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
listServiceRequestsByBooking(vars: ListServiceRequestsByBookingVariables, options?: ExecuteQueryOptions): QueryPromise<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;

interface ListServiceRequestsByBookingRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: ListServiceRequestsByBookingVariables): QueryRef<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;
}
export const listServiceRequestsByBookingRef: ListServiceRequestsByBookingRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `QueryRef` function.
```typescript
listServiceRequestsByBooking(dc: DataConnect, vars: ListServiceRequestsByBookingVariables, options?: ExecuteQueryOptions): QueryPromise<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;

interface ListServiceRequestsByBookingRef {
  ...
  (dc: DataConnect, vars: ListServiceRequestsByBookingVariables): QueryRef<ListServiceRequestsByBookingData, ListServiceRequestsByBookingVariables>;
}
export const listServiceRequestsByBookingRef: ListServiceRequestsByBookingRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the listServiceRequestsByBookingRef:
```typescript
const name = listServiceRequestsByBookingRef.operationName;
console.log(name);
```

### Variables
The `ListServiceRequestsByBooking` query requires an argument of type `ListServiceRequestsByBookingVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface ListServiceRequestsByBookingVariables {
  bookingId: UUIDString;
}
```
### Return Type
Recall that executing the `ListServiceRequestsByBooking` query returns a `QueryPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `ListServiceRequestsByBookingData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface ListServiceRequestsByBookingData {
  serviceRequests: ({
    description: string;
    status: string;
  })[];
}
```
### Using `ListServiceRequestsByBooking`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, listServiceRequestsByBooking, ListServiceRequestsByBookingVariables } from '@dataconnect/generated';

// The `ListServiceRequestsByBooking` query requires an argument of type `ListServiceRequestsByBookingVariables`:
const listServiceRequestsByBookingVars: ListServiceRequestsByBookingVariables = {
  bookingId: ..., 
};

// Call the `listServiceRequestsByBooking()` function to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await listServiceRequestsByBooking(listServiceRequestsByBookingVars);
// Variables can be defined inline as well.
const { data } = await listServiceRequestsByBooking({ bookingId: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await listServiceRequestsByBooking(dataConnect, listServiceRequestsByBookingVars);

console.log(data.serviceRequests);

// Or, you can use the `Promise` API.
listServiceRequestsByBooking(listServiceRequestsByBookingVars).then((response) => {
  const data = response.data;
  console.log(data.serviceRequests);
});
```

### Using `ListServiceRequestsByBooking`'s `QueryRef` function

```typescript
import { getDataConnect, executeQuery } from 'firebase/data-connect';
import { connectorConfig, listServiceRequestsByBookingRef, ListServiceRequestsByBookingVariables } from '@dataconnect/generated';

// The `ListServiceRequestsByBooking` query requires an argument of type `ListServiceRequestsByBookingVariables`:
const listServiceRequestsByBookingVars: ListServiceRequestsByBookingVariables = {
  bookingId: ..., 
};

// Call the `listServiceRequestsByBookingRef()` function to get a reference to the query.
const ref = listServiceRequestsByBookingRef(listServiceRequestsByBookingVars);
// Variables can be defined inline as well.
const ref = listServiceRequestsByBookingRef({ bookingId: ..., });

// You can also pass in a `DataConnect` instance to the `QueryRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = listServiceRequestsByBookingRef(dataConnect, listServiceRequestsByBookingVars);

// Call `executeQuery()` on the reference to execute the query.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeQuery(ref);

console.log(data.serviceRequests);

// Or, you can use the `Promise` API.
executeQuery(ref).then((response) => {
  const data = response.data;
  console.log(data.serviceRequests);
});
```

# Mutations

There are two ways to execute a Data Connect Mutation using the generated Web SDK:
- Using a Mutation Reference function, which returns a `MutationRef`
  - The `MutationRef` can be used as an argument to `executeMutation()`, which will execute the Mutation and return a `MutationPromise`
- Using an action shortcut function, which returns a `MutationPromise`
  - Calling the action shortcut function will execute the Mutation and return a `MutationPromise`

The following is true for both the action shortcut function and the `MutationRef` function:
- The `MutationPromise` returned will resolve to the result of the Mutation once it has finished executing
- If the Mutation accepts arguments, both the action shortcut function and the `MutationRef` function accept a single argument: an object that contains all the required variables (and the optional variables) for the Mutation
- Both functions can be called with or without passing in a `DataConnect` instance as an argument. If no `DataConnect` argument is passed in, then the generated SDK will call `getDataConnect(connectorConfig)` behind the scenes for you.

Below are examples of how to use the `example` connector's generated functions to execute each mutation. You can also follow the examples from the [Data Connect documentation](https://firebase.google.com/docs/data-connect/web-sdk#using-mutations).

## CreateHotel
You can execute the `CreateHotel` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createHotel(): MutationPromise<CreateHotelData, undefined>;

interface CreateHotelRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (): MutationRef<CreateHotelData, undefined>;
}
export const createHotelRef: CreateHotelRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createHotel(dc: DataConnect): MutationPromise<CreateHotelData, undefined>;

interface CreateHotelRef {
  ...
  (dc: DataConnect): MutationRef<CreateHotelData, undefined>;
}
export const createHotelRef: CreateHotelRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createHotelRef:
```typescript
const name = createHotelRef.operationName;
console.log(name);
```

### Variables
The `CreateHotel` mutation has no variables.
### Return Type
Recall that executing the `CreateHotel` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateHotelData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateHotelData {
  hotel_insert: Hotel_Key;
}
```
### Using `CreateHotel`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createHotel } from '@dataconnect/generated';


// Call the `createHotel()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createHotel();

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createHotel(dataConnect);

console.log(data.hotel_insert);

// Or, you can use the `Promise` API.
createHotel().then((response) => {
  const data = response.data;
  console.log(data.hotel_insert);
});
```

### Using `CreateHotel`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createHotelRef } from '@dataconnect/generated';


// Call the `createHotelRef()` function to get a reference to the mutation.
const ref = createHotelRef();

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createHotelRef(dataConnect);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.hotel_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.hotel_insert);
});
```

## UpdateHotel
You can execute the `UpdateHotel` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
updateHotel(vars: UpdateHotelVariables): MutationPromise<UpdateHotelData, UpdateHotelVariables>;

interface UpdateHotelRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateHotelVariables): MutationRef<UpdateHotelData, UpdateHotelVariables>;
}
export const updateHotelRef: UpdateHotelRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
updateHotel(dc: DataConnect, vars: UpdateHotelVariables): MutationPromise<UpdateHotelData, UpdateHotelVariables>;

interface UpdateHotelRef {
  ...
  (dc: DataConnect, vars: UpdateHotelVariables): MutationRef<UpdateHotelData, UpdateHotelVariables>;
}
export const updateHotelRef: UpdateHotelRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the updateHotelRef:
```typescript
const name = updateHotelRef.operationName;
console.log(name);
```

### Variables
The `UpdateHotel` mutation requires an argument of type `UpdateHotelVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface UpdateHotelVariables {
  id: UUIDString;
  name?: string | null;
}
```
### Return Type
Recall that executing the `UpdateHotel` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `UpdateHotelData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface UpdateHotelData {
  hotel_update?: Hotel_Key | null;
}
```
### Using `UpdateHotel`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, updateHotel, UpdateHotelVariables } from '@dataconnect/generated';

// The `UpdateHotel` mutation requires an argument of type `UpdateHotelVariables`:
const updateHotelVars: UpdateHotelVariables = {
  id: ..., 
  name: ..., // optional
};

// Call the `updateHotel()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await updateHotel(updateHotelVars);
// Variables can be defined inline as well.
const { data } = await updateHotel({ id: ..., name: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await updateHotel(dataConnect, updateHotelVars);

console.log(data.hotel_update);

// Or, you can use the `Promise` API.
updateHotel(updateHotelVars).then((response) => {
  const data = response.data;
  console.log(data.hotel_update);
});
```

### Using `UpdateHotel`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, updateHotelRef, UpdateHotelVariables } from '@dataconnect/generated';

// The `UpdateHotel` mutation requires an argument of type `UpdateHotelVariables`:
const updateHotelVars: UpdateHotelVariables = {
  id: ..., 
  name: ..., // optional
};

// Call the `updateHotelRef()` function to get a reference to the mutation.
const ref = updateHotelRef(updateHotelVars);
// Variables can be defined inline as well.
const ref = updateHotelRef({ id: ..., name: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = updateHotelRef(dataConnect, updateHotelVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.hotel_update);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.hotel_update);
});
```

## DeleteHotel
You can execute the `DeleteHotel` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
deleteHotel(vars: DeleteHotelVariables): MutationPromise<DeleteHotelData, DeleteHotelVariables>;

interface DeleteHotelRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteHotelVariables): MutationRef<DeleteHotelData, DeleteHotelVariables>;
}
export const deleteHotelRef: DeleteHotelRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
deleteHotel(dc: DataConnect, vars: DeleteHotelVariables): MutationPromise<DeleteHotelData, DeleteHotelVariables>;

interface DeleteHotelRef {
  ...
  (dc: DataConnect, vars: DeleteHotelVariables): MutationRef<DeleteHotelData, DeleteHotelVariables>;
}
export const deleteHotelRef: DeleteHotelRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the deleteHotelRef:
```typescript
const name = deleteHotelRef.operationName;
console.log(name);
```

### Variables
The `DeleteHotel` mutation requires an argument of type `DeleteHotelVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface DeleteHotelVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `DeleteHotel` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `DeleteHotelData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface DeleteHotelData {
  hotel_delete?: Hotel_Key | null;
}
```
### Using `DeleteHotel`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, deleteHotel, DeleteHotelVariables } from '@dataconnect/generated';

// The `DeleteHotel` mutation requires an argument of type `DeleteHotelVariables`:
const deleteHotelVars: DeleteHotelVariables = {
  id: ..., 
};

// Call the `deleteHotel()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await deleteHotel(deleteHotelVars);
// Variables can be defined inline as well.
const { data } = await deleteHotel({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await deleteHotel(dataConnect, deleteHotelVars);

console.log(data.hotel_delete);

// Or, you can use the `Promise` API.
deleteHotel(deleteHotelVars).then((response) => {
  const data = response.data;
  console.log(data.hotel_delete);
});
```

### Using `DeleteHotel`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, deleteHotelRef, DeleteHotelVariables } from '@dataconnect/generated';

// The `DeleteHotel` mutation requires an argument of type `DeleteHotelVariables`:
const deleteHotelVars: DeleteHotelVariables = {
  id: ..., 
};

// Call the `deleteHotelRef()` function to get a reference to the mutation.
const ref = deleteHotelRef(deleteHotelVars);
// Variables can be defined inline as well.
const ref = deleteHotelRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = deleteHotelRef(dataConnect, deleteHotelVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.hotel_delete);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.hotel_delete);
});
```

## CreateRoom
You can execute the `CreateRoom` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createRoom(vars: CreateRoomVariables): MutationPromise<CreateRoomData, CreateRoomVariables>;

interface CreateRoomRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateRoomVariables): MutationRef<CreateRoomData, CreateRoomVariables>;
}
export const createRoomRef: CreateRoomRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createRoom(dc: DataConnect, vars: CreateRoomVariables): MutationPromise<CreateRoomData, CreateRoomVariables>;

interface CreateRoomRef {
  ...
  (dc: DataConnect, vars: CreateRoomVariables): MutationRef<CreateRoomData, CreateRoomVariables>;
}
export const createRoomRef: CreateRoomRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createRoomRef:
```typescript
const name = createRoomRef.operationName;
console.log(name);
```

### Variables
The `CreateRoom` mutation requires an argument of type `CreateRoomVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateRoomVariables {
  hotelId: UUIDString;
  roomNumber: string;
  type: string;
  status: string;
}
```
### Return Type
Recall that executing the `CreateRoom` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateRoomData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateRoomData {
  room_insert: Room_Key;
}
```
### Using `CreateRoom`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createRoom, CreateRoomVariables } from '@dataconnect/generated';

// The `CreateRoom` mutation requires an argument of type `CreateRoomVariables`:
const createRoomVars: CreateRoomVariables = {
  hotelId: ..., 
  roomNumber: ..., 
  type: ..., 
  status: ..., 
};

// Call the `createRoom()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createRoom(createRoomVars);
// Variables can be defined inline as well.
const { data } = await createRoom({ hotelId: ..., roomNumber: ..., type: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createRoom(dataConnect, createRoomVars);

console.log(data.room_insert);

// Or, you can use the `Promise` API.
createRoom(createRoomVars).then((response) => {
  const data = response.data;
  console.log(data.room_insert);
});
```

### Using `CreateRoom`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createRoomRef, CreateRoomVariables } from '@dataconnect/generated';

// The `CreateRoom` mutation requires an argument of type `CreateRoomVariables`:
const createRoomVars: CreateRoomVariables = {
  hotelId: ..., 
  roomNumber: ..., 
  type: ..., 
  status: ..., 
};

// Call the `createRoomRef()` function to get a reference to the mutation.
const ref = createRoomRef(createRoomVars);
// Variables can be defined inline as well.
const ref = createRoomRef({ hotelId: ..., roomNumber: ..., type: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createRoomRef(dataConnect, createRoomVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.room_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.room_insert);
});
```

## UpdateRoom
You can execute the `UpdateRoom` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
updateRoom(vars: UpdateRoomVariables): MutationPromise<UpdateRoomData, UpdateRoomVariables>;

interface UpdateRoomRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateRoomVariables): MutationRef<UpdateRoomData, UpdateRoomVariables>;
}
export const updateRoomRef: UpdateRoomRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
updateRoom(dc: DataConnect, vars: UpdateRoomVariables): MutationPromise<UpdateRoomData, UpdateRoomVariables>;

interface UpdateRoomRef {
  ...
  (dc: DataConnect, vars: UpdateRoomVariables): MutationRef<UpdateRoomData, UpdateRoomVariables>;
}
export const updateRoomRef: UpdateRoomRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the updateRoomRef:
```typescript
const name = updateRoomRef.operationName;
console.log(name);
```

### Variables
The `UpdateRoom` mutation requires an argument of type `UpdateRoomVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface UpdateRoomVariables {
  id: UUIDString;
  status?: string | null;
}
```
### Return Type
Recall that executing the `UpdateRoom` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `UpdateRoomData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface UpdateRoomData {
  room_update?: Room_Key | null;
}
```
### Using `UpdateRoom`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, updateRoom, UpdateRoomVariables } from '@dataconnect/generated';

// The `UpdateRoom` mutation requires an argument of type `UpdateRoomVariables`:
const updateRoomVars: UpdateRoomVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateRoom()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await updateRoom(updateRoomVars);
// Variables can be defined inline as well.
const { data } = await updateRoom({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await updateRoom(dataConnect, updateRoomVars);

console.log(data.room_update);

// Or, you can use the `Promise` API.
updateRoom(updateRoomVars).then((response) => {
  const data = response.data;
  console.log(data.room_update);
});
```

### Using `UpdateRoom`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, updateRoomRef, UpdateRoomVariables } from '@dataconnect/generated';

// The `UpdateRoom` mutation requires an argument of type `UpdateRoomVariables`:
const updateRoomVars: UpdateRoomVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateRoomRef()` function to get a reference to the mutation.
const ref = updateRoomRef(updateRoomVars);
// Variables can be defined inline as well.
const ref = updateRoomRef({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = updateRoomRef(dataConnect, updateRoomVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.room_update);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.room_update);
});
```

## DeleteRoom
You can execute the `DeleteRoom` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
deleteRoom(vars: DeleteRoomVariables): MutationPromise<DeleteRoomData, DeleteRoomVariables>;

interface DeleteRoomRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteRoomVariables): MutationRef<DeleteRoomData, DeleteRoomVariables>;
}
export const deleteRoomRef: DeleteRoomRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
deleteRoom(dc: DataConnect, vars: DeleteRoomVariables): MutationPromise<DeleteRoomData, DeleteRoomVariables>;

interface DeleteRoomRef {
  ...
  (dc: DataConnect, vars: DeleteRoomVariables): MutationRef<DeleteRoomData, DeleteRoomVariables>;
}
export const deleteRoomRef: DeleteRoomRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the deleteRoomRef:
```typescript
const name = deleteRoomRef.operationName;
console.log(name);
```

### Variables
The `DeleteRoom` mutation requires an argument of type `DeleteRoomVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface DeleteRoomVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `DeleteRoom` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `DeleteRoomData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface DeleteRoomData {
  room_delete?: Room_Key | null;
}
```
### Using `DeleteRoom`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, deleteRoom, DeleteRoomVariables } from '@dataconnect/generated';

// The `DeleteRoom` mutation requires an argument of type `DeleteRoomVariables`:
const deleteRoomVars: DeleteRoomVariables = {
  id: ..., 
};

// Call the `deleteRoom()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await deleteRoom(deleteRoomVars);
// Variables can be defined inline as well.
const { data } = await deleteRoom({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await deleteRoom(dataConnect, deleteRoomVars);

console.log(data.room_delete);

// Or, you can use the `Promise` API.
deleteRoom(deleteRoomVars).then((response) => {
  const data = response.data;
  console.log(data.room_delete);
});
```

### Using `DeleteRoom`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, deleteRoomRef, DeleteRoomVariables } from '@dataconnect/generated';

// The `DeleteRoom` mutation requires an argument of type `DeleteRoomVariables`:
const deleteRoomVars: DeleteRoomVariables = {
  id: ..., 
};

// Call the `deleteRoomRef()` function to get a reference to the mutation.
const ref = deleteRoomRef(deleteRoomVars);
// Variables can be defined inline as well.
const ref = deleteRoomRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = deleteRoomRef(dataConnect, deleteRoomVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.room_delete);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.room_delete);
});
```

## CreateGuest
You can execute the `CreateGuest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createGuest(vars: CreateGuestVariables): MutationPromise<CreateGuestData, CreateGuestVariables>;

interface CreateGuestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateGuestVariables): MutationRef<CreateGuestData, CreateGuestVariables>;
}
export const createGuestRef: CreateGuestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createGuest(dc: DataConnect, vars: CreateGuestVariables): MutationPromise<CreateGuestData, CreateGuestVariables>;

interface CreateGuestRef {
  ...
  (dc: DataConnect, vars: CreateGuestVariables): MutationRef<CreateGuestData, CreateGuestVariables>;
}
export const createGuestRef: CreateGuestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createGuestRef:
```typescript
const name = createGuestRef.operationName;
console.log(name);
```

### Variables
The `CreateGuest` mutation requires an argument of type `CreateGuestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateGuestVariables {
  fullName: string;
  email: string;
  phone: string;
}
```
### Return Type
Recall that executing the `CreateGuest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateGuestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateGuestData {
  guest_insert: Guest_Key;
}
```
### Using `CreateGuest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createGuest, CreateGuestVariables } from '@dataconnect/generated';

// The `CreateGuest` mutation requires an argument of type `CreateGuestVariables`:
const createGuestVars: CreateGuestVariables = {
  fullName: ..., 
  email: ..., 
  phone: ..., 
};

// Call the `createGuest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createGuest(createGuestVars);
// Variables can be defined inline as well.
const { data } = await createGuest({ fullName: ..., email: ..., phone: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createGuest(dataConnect, createGuestVars);

console.log(data.guest_insert);

// Or, you can use the `Promise` API.
createGuest(createGuestVars).then((response) => {
  const data = response.data;
  console.log(data.guest_insert);
});
```

### Using `CreateGuest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createGuestRef, CreateGuestVariables } from '@dataconnect/generated';

// The `CreateGuest` mutation requires an argument of type `CreateGuestVariables`:
const createGuestVars: CreateGuestVariables = {
  fullName: ..., 
  email: ..., 
  phone: ..., 
};

// Call the `createGuestRef()` function to get a reference to the mutation.
const ref = createGuestRef(createGuestVars);
// Variables can be defined inline as well.
const ref = createGuestRef({ fullName: ..., email: ..., phone: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createGuestRef(dataConnect, createGuestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.guest_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.guest_insert);
});
```

## UpdateGuest
You can execute the `UpdateGuest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
updateGuest(vars: UpdateGuestVariables): MutationPromise<UpdateGuestData, UpdateGuestVariables>;

interface UpdateGuestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateGuestVariables): MutationRef<UpdateGuestData, UpdateGuestVariables>;
}
export const updateGuestRef: UpdateGuestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
updateGuest(dc: DataConnect, vars: UpdateGuestVariables): MutationPromise<UpdateGuestData, UpdateGuestVariables>;

interface UpdateGuestRef {
  ...
  (dc: DataConnect, vars: UpdateGuestVariables): MutationRef<UpdateGuestData, UpdateGuestVariables>;
}
export const updateGuestRef: UpdateGuestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the updateGuestRef:
```typescript
const name = updateGuestRef.operationName;
console.log(name);
```

### Variables
The `UpdateGuest` mutation requires an argument of type `UpdateGuestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface UpdateGuestVariables {
  id: UUIDString;
  phone?: string | null;
}
```
### Return Type
Recall that executing the `UpdateGuest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `UpdateGuestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface UpdateGuestData {
  guest_update?: Guest_Key | null;
}
```
### Using `UpdateGuest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, updateGuest, UpdateGuestVariables } from '@dataconnect/generated';

// The `UpdateGuest` mutation requires an argument of type `UpdateGuestVariables`:
const updateGuestVars: UpdateGuestVariables = {
  id: ..., 
  phone: ..., // optional
};

// Call the `updateGuest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await updateGuest(updateGuestVars);
// Variables can be defined inline as well.
const { data } = await updateGuest({ id: ..., phone: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await updateGuest(dataConnect, updateGuestVars);

console.log(data.guest_update);

// Or, you can use the `Promise` API.
updateGuest(updateGuestVars).then((response) => {
  const data = response.data;
  console.log(data.guest_update);
});
```

### Using `UpdateGuest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, updateGuestRef, UpdateGuestVariables } from '@dataconnect/generated';

// The `UpdateGuest` mutation requires an argument of type `UpdateGuestVariables`:
const updateGuestVars: UpdateGuestVariables = {
  id: ..., 
  phone: ..., // optional
};

// Call the `updateGuestRef()` function to get a reference to the mutation.
const ref = updateGuestRef(updateGuestVars);
// Variables can be defined inline as well.
const ref = updateGuestRef({ id: ..., phone: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = updateGuestRef(dataConnect, updateGuestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.guest_update);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.guest_update);
});
```

## DeleteGuest
You can execute the `DeleteGuest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
deleteGuest(vars: DeleteGuestVariables): MutationPromise<DeleteGuestData, DeleteGuestVariables>;

interface DeleteGuestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteGuestVariables): MutationRef<DeleteGuestData, DeleteGuestVariables>;
}
export const deleteGuestRef: DeleteGuestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
deleteGuest(dc: DataConnect, vars: DeleteGuestVariables): MutationPromise<DeleteGuestData, DeleteGuestVariables>;

interface DeleteGuestRef {
  ...
  (dc: DataConnect, vars: DeleteGuestVariables): MutationRef<DeleteGuestData, DeleteGuestVariables>;
}
export const deleteGuestRef: DeleteGuestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the deleteGuestRef:
```typescript
const name = deleteGuestRef.operationName;
console.log(name);
```

### Variables
The `DeleteGuest` mutation requires an argument of type `DeleteGuestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface DeleteGuestVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `DeleteGuest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `DeleteGuestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface DeleteGuestData {
  guest_delete?: Guest_Key | null;
}
```
### Using `DeleteGuest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, deleteGuest, DeleteGuestVariables } from '@dataconnect/generated';

// The `DeleteGuest` mutation requires an argument of type `DeleteGuestVariables`:
const deleteGuestVars: DeleteGuestVariables = {
  id: ..., 
};

// Call the `deleteGuest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await deleteGuest(deleteGuestVars);
// Variables can be defined inline as well.
const { data } = await deleteGuest({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await deleteGuest(dataConnect, deleteGuestVars);

console.log(data.guest_delete);

// Or, you can use the `Promise` API.
deleteGuest(deleteGuestVars).then((response) => {
  const data = response.data;
  console.log(data.guest_delete);
});
```

### Using `DeleteGuest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, deleteGuestRef, DeleteGuestVariables } from '@dataconnect/generated';

// The `DeleteGuest` mutation requires an argument of type `DeleteGuestVariables`:
const deleteGuestVars: DeleteGuestVariables = {
  id: ..., 
};

// Call the `deleteGuestRef()` function to get a reference to the mutation.
const ref = deleteGuestRef(deleteGuestVars);
// Variables can be defined inline as well.
const ref = deleteGuestRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = deleteGuestRef(dataConnect, deleteGuestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.guest_delete);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.guest_delete);
});
```

## CreateBooking
You can execute the `CreateBooking` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createBooking(vars: CreateBookingVariables): MutationPromise<CreateBookingData, CreateBookingVariables>;

interface CreateBookingRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateBookingVariables): MutationRef<CreateBookingData, CreateBookingVariables>;
}
export const createBookingRef: CreateBookingRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createBooking(dc: DataConnect, vars: CreateBookingVariables): MutationPromise<CreateBookingData, CreateBookingVariables>;

interface CreateBookingRef {
  ...
  (dc: DataConnect, vars: CreateBookingVariables): MutationRef<CreateBookingData, CreateBookingVariables>;
}
export const createBookingRef: CreateBookingRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createBookingRef:
```typescript
const name = createBookingRef.operationName;
console.log(name);
```

### Variables
The `CreateBooking` mutation requires an argument of type `CreateBookingVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateBookingVariables {
  guestId: UUIDString;
  hotelId: UUIDString;
  roomId: UUIDString;
  checkIn: DateString;
  checkOut: DateString;
  status: string;
}
```
### Return Type
Recall that executing the `CreateBooking` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateBookingData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateBookingData {
  booking_insert: Booking_Key;
}
```
### Using `CreateBooking`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createBooking, CreateBookingVariables } from '@dataconnect/generated';

// The `CreateBooking` mutation requires an argument of type `CreateBookingVariables`:
const createBookingVars: CreateBookingVariables = {
  guestId: ..., 
  hotelId: ..., 
  roomId: ..., 
  checkIn: ..., 
  checkOut: ..., 
  status: ..., 
};

// Call the `createBooking()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createBooking(createBookingVars);
// Variables can be defined inline as well.
const { data } = await createBooking({ guestId: ..., hotelId: ..., roomId: ..., checkIn: ..., checkOut: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createBooking(dataConnect, createBookingVars);

console.log(data.booking_insert);

// Or, you can use the `Promise` API.
createBooking(createBookingVars).then((response) => {
  const data = response.data;
  console.log(data.booking_insert);
});
```

### Using `CreateBooking`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createBookingRef, CreateBookingVariables } from '@dataconnect/generated';

// The `CreateBooking` mutation requires an argument of type `CreateBookingVariables`:
const createBookingVars: CreateBookingVariables = {
  guestId: ..., 
  hotelId: ..., 
  roomId: ..., 
  checkIn: ..., 
  checkOut: ..., 
  status: ..., 
};

// Call the `createBookingRef()` function to get a reference to the mutation.
const ref = createBookingRef(createBookingVars);
// Variables can be defined inline as well.
const ref = createBookingRef({ guestId: ..., hotelId: ..., roomId: ..., checkIn: ..., checkOut: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createBookingRef(dataConnect, createBookingVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.booking_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.booking_insert);
});
```

## UpdateBooking
You can execute the `UpdateBooking` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
updateBooking(vars: UpdateBookingVariables): MutationPromise<UpdateBookingData, UpdateBookingVariables>;

interface UpdateBookingRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateBookingVariables): MutationRef<UpdateBookingData, UpdateBookingVariables>;
}
export const updateBookingRef: UpdateBookingRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
updateBooking(dc: DataConnect, vars: UpdateBookingVariables): MutationPromise<UpdateBookingData, UpdateBookingVariables>;

interface UpdateBookingRef {
  ...
  (dc: DataConnect, vars: UpdateBookingVariables): MutationRef<UpdateBookingData, UpdateBookingVariables>;
}
export const updateBookingRef: UpdateBookingRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the updateBookingRef:
```typescript
const name = updateBookingRef.operationName;
console.log(name);
```

### Variables
The `UpdateBooking` mutation requires an argument of type `UpdateBookingVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface UpdateBookingVariables {
  id: UUIDString;
  status?: string | null;
}
```
### Return Type
Recall that executing the `UpdateBooking` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `UpdateBookingData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface UpdateBookingData {
  booking_update?: Booking_Key | null;
}
```
### Using `UpdateBooking`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, updateBooking, UpdateBookingVariables } from '@dataconnect/generated';

// The `UpdateBooking` mutation requires an argument of type `UpdateBookingVariables`:
const updateBookingVars: UpdateBookingVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateBooking()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await updateBooking(updateBookingVars);
// Variables can be defined inline as well.
const { data } = await updateBooking({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await updateBooking(dataConnect, updateBookingVars);

console.log(data.booking_update);

// Or, you can use the `Promise` API.
updateBooking(updateBookingVars).then((response) => {
  const data = response.data;
  console.log(data.booking_update);
});
```

### Using `UpdateBooking`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, updateBookingRef, UpdateBookingVariables } from '@dataconnect/generated';

// The `UpdateBooking` mutation requires an argument of type `UpdateBookingVariables`:
const updateBookingVars: UpdateBookingVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateBookingRef()` function to get a reference to the mutation.
const ref = updateBookingRef(updateBookingVars);
// Variables can be defined inline as well.
const ref = updateBookingRef({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = updateBookingRef(dataConnect, updateBookingVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.booking_update);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.booking_update);
});
```

## DeleteBooking
You can execute the `DeleteBooking` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
deleteBooking(vars: DeleteBookingVariables): MutationPromise<DeleteBookingData, DeleteBookingVariables>;

interface DeleteBookingRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteBookingVariables): MutationRef<DeleteBookingData, DeleteBookingVariables>;
}
export const deleteBookingRef: DeleteBookingRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
deleteBooking(dc: DataConnect, vars: DeleteBookingVariables): MutationPromise<DeleteBookingData, DeleteBookingVariables>;

interface DeleteBookingRef {
  ...
  (dc: DataConnect, vars: DeleteBookingVariables): MutationRef<DeleteBookingData, DeleteBookingVariables>;
}
export const deleteBookingRef: DeleteBookingRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the deleteBookingRef:
```typescript
const name = deleteBookingRef.operationName;
console.log(name);
```

### Variables
The `DeleteBooking` mutation requires an argument of type `DeleteBookingVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface DeleteBookingVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `DeleteBooking` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `DeleteBookingData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface DeleteBookingData {
  booking_delete?: Booking_Key | null;
}
```
### Using `DeleteBooking`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, deleteBooking, DeleteBookingVariables } from '@dataconnect/generated';

// The `DeleteBooking` mutation requires an argument of type `DeleteBookingVariables`:
const deleteBookingVars: DeleteBookingVariables = {
  id: ..., 
};

// Call the `deleteBooking()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await deleteBooking(deleteBookingVars);
// Variables can be defined inline as well.
const { data } = await deleteBooking({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await deleteBooking(dataConnect, deleteBookingVars);

console.log(data.booking_delete);

// Or, you can use the `Promise` API.
deleteBooking(deleteBookingVars).then((response) => {
  const data = response.data;
  console.log(data.booking_delete);
});
```

### Using `DeleteBooking`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, deleteBookingRef, DeleteBookingVariables } from '@dataconnect/generated';

// The `DeleteBooking` mutation requires an argument of type `DeleteBookingVariables`:
const deleteBookingVars: DeleteBookingVariables = {
  id: ..., 
};

// Call the `deleteBookingRef()` function to get a reference to the mutation.
const ref = deleteBookingRef(deleteBookingVars);
// Variables can be defined inline as well.
const ref = deleteBookingRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = deleteBookingRef(dataConnect, deleteBookingVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.booking_delete);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.booking_delete);
});
```

## CreateServiceRequest
You can execute the `CreateServiceRequest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
createServiceRequest(vars: CreateServiceRequestVariables): MutationPromise<CreateServiceRequestData, CreateServiceRequestVariables>;

interface CreateServiceRequestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: CreateServiceRequestVariables): MutationRef<CreateServiceRequestData, CreateServiceRequestVariables>;
}
export const createServiceRequestRef: CreateServiceRequestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
createServiceRequest(dc: DataConnect, vars: CreateServiceRequestVariables): MutationPromise<CreateServiceRequestData, CreateServiceRequestVariables>;

interface CreateServiceRequestRef {
  ...
  (dc: DataConnect, vars: CreateServiceRequestVariables): MutationRef<CreateServiceRequestData, CreateServiceRequestVariables>;
}
export const createServiceRequestRef: CreateServiceRequestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the createServiceRequestRef:
```typescript
const name = createServiceRequestRef.operationName;
console.log(name);
```

### Variables
The `CreateServiceRequest` mutation requires an argument of type `CreateServiceRequestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface CreateServiceRequestVariables {
  bookingId: UUIDString;
  desc: string;
  status: string;
}
```
### Return Type
Recall that executing the `CreateServiceRequest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `CreateServiceRequestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface CreateServiceRequestData {
  serviceRequest_insert: ServiceRequest_Key;
}
```
### Using `CreateServiceRequest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, createServiceRequest, CreateServiceRequestVariables } from '@dataconnect/generated';

// The `CreateServiceRequest` mutation requires an argument of type `CreateServiceRequestVariables`:
const createServiceRequestVars: CreateServiceRequestVariables = {
  bookingId: ..., 
  desc: ..., 
  status: ..., 
};

// Call the `createServiceRequest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await createServiceRequest(createServiceRequestVars);
// Variables can be defined inline as well.
const { data } = await createServiceRequest({ bookingId: ..., desc: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await createServiceRequest(dataConnect, createServiceRequestVars);

console.log(data.serviceRequest_insert);

// Or, you can use the `Promise` API.
createServiceRequest(createServiceRequestVars).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_insert);
});
```

### Using `CreateServiceRequest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, createServiceRequestRef, CreateServiceRequestVariables } from '@dataconnect/generated';

// The `CreateServiceRequest` mutation requires an argument of type `CreateServiceRequestVariables`:
const createServiceRequestVars: CreateServiceRequestVariables = {
  bookingId: ..., 
  desc: ..., 
  status: ..., 
};

// Call the `createServiceRequestRef()` function to get a reference to the mutation.
const ref = createServiceRequestRef(createServiceRequestVars);
// Variables can be defined inline as well.
const ref = createServiceRequestRef({ bookingId: ..., desc: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = createServiceRequestRef(dataConnect, createServiceRequestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.serviceRequest_insert);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_insert);
});
```

## UpdateServiceRequest
You can execute the `UpdateServiceRequest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
updateServiceRequest(vars: UpdateServiceRequestVariables): MutationPromise<UpdateServiceRequestData, UpdateServiceRequestVariables>;

interface UpdateServiceRequestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: UpdateServiceRequestVariables): MutationRef<UpdateServiceRequestData, UpdateServiceRequestVariables>;
}
export const updateServiceRequestRef: UpdateServiceRequestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
updateServiceRequest(dc: DataConnect, vars: UpdateServiceRequestVariables): MutationPromise<UpdateServiceRequestData, UpdateServiceRequestVariables>;

interface UpdateServiceRequestRef {
  ...
  (dc: DataConnect, vars: UpdateServiceRequestVariables): MutationRef<UpdateServiceRequestData, UpdateServiceRequestVariables>;
}
export const updateServiceRequestRef: UpdateServiceRequestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the updateServiceRequestRef:
```typescript
const name = updateServiceRequestRef.operationName;
console.log(name);
```

### Variables
The `UpdateServiceRequest` mutation requires an argument of type `UpdateServiceRequestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface UpdateServiceRequestVariables {
  id: UUIDString;
  status?: string | null;
}
```
### Return Type
Recall that executing the `UpdateServiceRequest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `UpdateServiceRequestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface UpdateServiceRequestData {
  serviceRequest_update?: ServiceRequest_Key | null;
}
```
### Using `UpdateServiceRequest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, updateServiceRequest, UpdateServiceRequestVariables } from '@dataconnect/generated';

// The `UpdateServiceRequest` mutation requires an argument of type `UpdateServiceRequestVariables`:
const updateServiceRequestVars: UpdateServiceRequestVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateServiceRequest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await updateServiceRequest(updateServiceRequestVars);
// Variables can be defined inline as well.
const { data } = await updateServiceRequest({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await updateServiceRequest(dataConnect, updateServiceRequestVars);

console.log(data.serviceRequest_update);

// Or, you can use the `Promise` API.
updateServiceRequest(updateServiceRequestVars).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_update);
});
```

### Using `UpdateServiceRequest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, updateServiceRequestRef, UpdateServiceRequestVariables } from '@dataconnect/generated';

// The `UpdateServiceRequest` mutation requires an argument of type `UpdateServiceRequestVariables`:
const updateServiceRequestVars: UpdateServiceRequestVariables = {
  id: ..., 
  status: ..., // optional
};

// Call the `updateServiceRequestRef()` function to get a reference to the mutation.
const ref = updateServiceRequestRef(updateServiceRequestVars);
// Variables can be defined inline as well.
const ref = updateServiceRequestRef({ id: ..., status: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = updateServiceRequestRef(dataConnect, updateServiceRequestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.serviceRequest_update);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_update);
});
```

## DeleteServiceRequest
You can execute the `DeleteServiceRequest` mutation using the following action shortcut function, or by calling `executeMutation()` after calling the following `MutationRef` function, both of which are defined in [dataconnect-generated/index.d.ts](./index.d.ts):
```typescript
deleteServiceRequest(vars: DeleteServiceRequestVariables): MutationPromise<DeleteServiceRequestData, DeleteServiceRequestVariables>;

interface DeleteServiceRequestRef {
  ...
  /* Allow users to create refs without passing in DataConnect */
  (vars: DeleteServiceRequestVariables): MutationRef<DeleteServiceRequestData, DeleteServiceRequestVariables>;
}
export const deleteServiceRequestRef: DeleteServiceRequestRef;
```
You can also pass in a `DataConnect` instance to the action shortcut function or `MutationRef` function.
```typescript
deleteServiceRequest(dc: DataConnect, vars: DeleteServiceRequestVariables): MutationPromise<DeleteServiceRequestData, DeleteServiceRequestVariables>;

interface DeleteServiceRequestRef {
  ...
  (dc: DataConnect, vars: DeleteServiceRequestVariables): MutationRef<DeleteServiceRequestData, DeleteServiceRequestVariables>;
}
export const deleteServiceRequestRef: DeleteServiceRequestRef;
```

If you need the name of the operation without creating a ref, you can retrieve the operation name by calling the `operationName` property on the deleteServiceRequestRef:
```typescript
const name = deleteServiceRequestRef.operationName;
console.log(name);
```

### Variables
The `DeleteServiceRequest` mutation requires an argument of type `DeleteServiceRequestVariables`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:

```typescript
export interface DeleteServiceRequestVariables {
  id: UUIDString;
}
```
### Return Type
Recall that executing the `DeleteServiceRequest` mutation returns a `MutationPromise` that resolves to an object with a `data` property.

The `data` property is an object of type `DeleteServiceRequestData`, which is defined in [dataconnect-generated/index.d.ts](./index.d.ts). It has the following fields:
```typescript
export interface DeleteServiceRequestData {
  serviceRequest_delete?: ServiceRequest_Key | null;
}
```
### Using `DeleteServiceRequest`'s action shortcut function

```typescript
import { getDataConnect } from 'firebase/data-connect';
import { connectorConfig, deleteServiceRequest, DeleteServiceRequestVariables } from '@dataconnect/generated';

// The `DeleteServiceRequest` mutation requires an argument of type `DeleteServiceRequestVariables`:
const deleteServiceRequestVars: DeleteServiceRequestVariables = {
  id: ..., 
};

// Call the `deleteServiceRequest()` function to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await deleteServiceRequest(deleteServiceRequestVars);
// Variables can be defined inline as well.
const { data } = await deleteServiceRequest({ id: ..., });

// You can also pass in a `DataConnect` instance to the action shortcut function.
const dataConnect = getDataConnect(connectorConfig);
const { data } = await deleteServiceRequest(dataConnect, deleteServiceRequestVars);

console.log(data.serviceRequest_delete);

// Or, you can use the `Promise` API.
deleteServiceRequest(deleteServiceRequestVars).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_delete);
});
```

### Using `DeleteServiceRequest`'s `MutationRef` function

```typescript
import { getDataConnect, executeMutation } from 'firebase/data-connect';
import { connectorConfig, deleteServiceRequestRef, DeleteServiceRequestVariables } from '@dataconnect/generated';

// The `DeleteServiceRequest` mutation requires an argument of type `DeleteServiceRequestVariables`:
const deleteServiceRequestVars: DeleteServiceRequestVariables = {
  id: ..., 
};

// Call the `deleteServiceRequestRef()` function to get a reference to the mutation.
const ref = deleteServiceRequestRef(deleteServiceRequestVars);
// Variables can be defined inline as well.
const ref = deleteServiceRequestRef({ id: ..., });

// You can also pass in a `DataConnect` instance to the `MutationRef` function.
const dataConnect = getDataConnect(connectorConfig);
const ref = deleteServiceRequestRef(dataConnect, deleteServiceRequestVars);

// Call `executeMutation()` on the reference to execute the mutation.
// You can use the `await` keyword to wait for the promise to resolve.
const { data } = await executeMutation(ref);

console.log(data.serviceRequest_delete);

// Or, you can use the `Promise` API.
executeMutation(ref).then((response) => {
  const data = response.data;
  console.log(data.serviceRequest_delete);
});
```

