{
  description = "Flask project with isolated PostgreSQL";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          flask
          flask-sqlalchemy
          psycopg2
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.postgresql
          ];

          shellHook = ''
            export PGDATA="$PWD/.db"
            export PGHOST="127.0.0.1"
            export PGPORT=5432
            # Use your system username as the default admin
            export PGUSER="$USER" 

            if [ ! -d "$PGDATA" ]; then
              initdb --auth=trust --no-instructions -D "$PGDATA"
              echo "unix_socket_directories = '''" >> "$PGDATA/postgresql.conf"
              echo "listen_addresses = '127.0.0.1'" >> "$PGDATA/postgresql.conf"
            fi

            finish() {
              pg_ctl -D "$PGDATA" stop
            }
            trap finish EXIT

            if ! pg_ctl -D "$PGDATA" status > /dev/null; then
              pg_ctl -D "$PGDATA" -l "$PGDATA/postgres.log" -o "-h 127.0.0.1 -p $PGPORT" start
              sleep 2
            fi

            # Check for the aircraft_db user using the current system user ($USER)
            if ! psql -h 127.0.0.1 -U "$USER" -d postgres -c "SELECT 1 FROM pg_roles WHERE rolname='aircraft_db'" | grep -q 1; then
              createuser -h 127.0.0.1 -U "$USER" --no-password aircraft_db
            fi

            # Check for the aircraft_db database
            if ! psql -h 127.0.0.1 -U "$USER" -lqt | cut -d \| -f 1 | grep -qw aircraft_db; then
              createdb -h 127.0.0.1 -U "$USER" -O aircraft_db aircraft_db
            fi

            echo "PostgreSQL started on 127.0.0.1:$PGPORT"
            echo "Logged in as: $USER"
          '';
        };
      });
}