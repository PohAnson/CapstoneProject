"""Contains all the SQLcmds used."""

SQLcmds = {
    "create_bus_stops_table": """
    CREATE TABLE IF NOT EXISTS "bus_stops" (
        "bus_stop_code" TEXT,
        "road_name" TEXT, 
        "description" TEXT,
        "latitude" REAL,
        "longitude" REAL,
        PRIMARY KEY ("bus_stop_code")
    );
""",
    "create_bus_routes_table": """
    CREATE TABLE IF NOT EXISTS "bus_routes" (
        "service_no" TEXT,
        "direction" INTEGER,
        "stop_sequence" INTEGER,
        "bus_stop_code" TEXT,
        "distance" REAL,
        PRIMARY KEY ("service_no", "direction", "stop_sequence")
    );
""",
    "insert_bus_stops": """
    INSERT INTO "bus_stops" 
        VALUES (:bus_stop_code, :road_name, :description, :latitude, :longitude);
""",
    "insert_bus_routes": """
    INSERT INTO "bus_routes"
    VALUES (:service_no, :direction, :stop_sequence, :bus_stop_code, :distance );
""",
    "get_bus_routes": """
    SELECT * FROM "bus_routes";
""",
    "find_bus_stop_connectivity": """
    SELECT bus_stop_code FROM "bus_routes"
    WHERE "service_no"=? AND "direction"=? AND "stop_sequence">?;
""",
    "get_distance": """
    SELECT distance FROM "bus_routes"
    WHERE bus_stop_code=? AND service_no=? AND direction=?
    ORDER BY stop_sequence ASC;
""",
    "get_buses_at": """
    SELECT "service_no", "direction", "stop_sequence" FROM "bus_routes" 
    WHERE "bus_stop_code"=?;
""",
    "get_bus_stop_info": """
    SELECT * FROM "bus_stops"
    WHERE "bus_stop_code"=?
""",
}
