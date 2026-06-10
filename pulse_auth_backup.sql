--
-- PostgreSQL database dump
--

\restrict xm3PGpFXURMOfTQuWLCyp95Rulj9VpXAnzV9psPWTatINIuf8J4nBI8c15iDm5P

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_event_entity; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.admin_event_entity (
    id character varying(36) NOT NULL,
    admin_event_time bigint,
    realm_id character varying(255),
    operation_type character varying(255),
    auth_realm_id character varying(255),
    auth_client_id character varying(255),
    auth_user_id character varying(255),
    ip_address character varying(255),
    resource_path character varying(2550),
    representation text,
    error character varying(255),
    resource_type character varying(64)
);


ALTER TABLE public.admin_event_entity OWNER TO keycloak_user;

--
-- Name: associated_policy; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.associated_policy (
    policy_id character varying(36) NOT NULL,
    associated_policy_id character varying(36) NOT NULL
);


ALTER TABLE public.associated_policy OWNER TO keycloak_user;

--
-- Name: authentication_execution; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.authentication_execution (
    id character varying(36) NOT NULL,
    alias character varying(255),
    authenticator character varying(36),
    realm_id character varying(36),
    flow_id character varying(36),
    requirement integer,
    priority integer,
    authenticator_flow boolean DEFAULT false NOT NULL,
    auth_flow_id character varying(36),
    auth_config character varying(36)
);


ALTER TABLE public.authentication_execution OWNER TO keycloak_user;

--
-- Name: authentication_flow; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.authentication_flow (
    id character varying(36) NOT NULL,
    alias character varying(255),
    description character varying(255),
    realm_id character varying(36),
    provider_id character varying(36) DEFAULT 'basic-flow'::character varying NOT NULL,
    top_level boolean DEFAULT false NOT NULL,
    built_in boolean DEFAULT false NOT NULL
);


ALTER TABLE public.authentication_flow OWNER TO keycloak_user;

--
-- Name: authenticator_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.authenticator_config (
    id character varying(36) NOT NULL,
    alias character varying(255),
    realm_id character varying(36)
);


ALTER TABLE public.authenticator_config OWNER TO keycloak_user;

--
-- Name: authenticator_config_entry; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.authenticator_config_entry (
    authenticator_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.authenticator_config_entry OWNER TO keycloak_user;

--
-- Name: broker_link; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.broker_link (
    identity_provider character varying(255) NOT NULL,
    storage_provider_id character varying(255),
    realm_id character varying(36) NOT NULL,
    broker_user_id character varying(255),
    broker_username character varying(255),
    token text,
    user_id character varying(255) NOT NULL
);


ALTER TABLE public.broker_link OWNER TO keycloak_user;

--
-- Name: client; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client (
    id character varying(36) NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    full_scope_allowed boolean DEFAULT false NOT NULL,
    client_id character varying(255),
    not_before integer,
    public_client boolean DEFAULT false NOT NULL,
    secret character varying(255),
    base_url character varying(255),
    bearer_only boolean DEFAULT false NOT NULL,
    management_url character varying(255),
    surrogate_auth_required boolean DEFAULT false NOT NULL,
    realm_id character varying(36),
    protocol character varying(255),
    node_rereg_timeout integer DEFAULT 0,
    frontchannel_logout boolean DEFAULT false NOT NULL,
    consent_required boolean DEFAULT false NOT NULL,
    name character varying(255),
    service_accounts_enabled boolean DEFAULT false NOT NULL,
    client_authenticator_type character varying(255),
    root_url character varying(255),
    description character varying(255),
    registration_token character varying(255),
    standard_flow_enabled boolean DEFAULT true NOT NULL,
    implicit_flow_enabled boolean DEFAULT false NOT NULL,
    direct_access_grants_enabled boolean DEFAULT false NOT NULL,
    always_display_in_console boolean DEFAULT false NOT NULL
);


ALTER TABLE public.client OWNER TO keycloak_user;

--
-- Name: client_attributes; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_attributes (
    client_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.client_attributes OWNER TO keycloak_user;

--
-- Name: client_auth_flow_bindings; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_auth_flow_bindings (
    client_id character varying(36) NOT NULL,
    flow_id character varying(36),
    binding_name character varying(255) NOT NULL
);


ALTER TABLE public.client_auth_flow_bindings OWNER TO keycloak_user;

--
-- Name: client_initial_access; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_initial_access (
    id character varying(36) NOT NULL,
    realm_id character varying(36) NOT NULL,
    "timestamp" integer,
    expiration integer,
    count integer,
    remaining_count integer
);


ALTER TABLE public.client_initial_access OWNER TO keycloak_user;

--
-- Name: client_node_registrations; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_node_registrations (
    client_id character varying(36) NOT NULL,
    value integer,
    name character varying(255) NOT NULL
);


ALTER TABLE public.client_node_registrations OWNER TO keycloak_user;

--
-- Name: client_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_scope (
    id character varying(36) NOT NULL,
    name character varying(255),
    realm_id character varying(36),
    description character varying(255),
    protocol character varying(255)
);


ALTER TABLE public.client_scope OWNER TO keycloak_user;

--
-- Name: client_scope_attributes; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_scope_attributes (
    scope_id character varying(36) NOT NULL,
    value character varying(2048),
    name character varying(255) NOT NULL
);


ALTER TABLE public.client_scope_attributes OWNER TO keycloak_user;

--
-- Name: client_scope_client; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_scope_client (
    client_id character varying(255) NOT NULL,
    scope_id character varying(255) NOT NULL,
    default_scope boolean DEFAULT false NOT NULL
);


ALTER TABLE public.client_scope_client OWNER TO keycloak_user;

--
-- Name: client_scope_role_mapping; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_scope_role_mapping (
    scope_id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL
);


ALTER TABLE public.client_scope_role_mapping OWNER TO keycloak_user;

--
-- Name: client_session; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_session (
    id character varying(36) NOT NULL,
    client_id character varying(36),
    redirect_uri character varying(255),
    state character varying(255),
    "timestamp" integer,
    session_id character varying(36),
    auth_method character varying(255),
    realm_id character varying(255),
    auth_user_id character varying(36),
    current_action character varying(36)
);


ALTER TABLE public.client_session OWNER TO keycloak_user;

--
-- Name: client_session_auth_status; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_session_auth_status (
    authenticator character varying(36) NOT NULL,
    status integer,
    client_session character varying(36) NOT NULL
);


ALTER TABLE public.client_session_auth_status OWNER TO keycloak_user;

--
-- Name: client_session_note; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_session_note (
    name character varying(255) NOT NULL,
    value character varying(255),
    client_session character varying(36) NOT NULL
);


ALTER TABLE public.client_session_note OWNER TO keycloak_user;

--
-- Name: client_session_prot_mapper; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_session_prot_mapper (
    protocol_mapper_id character varying(36) NOT NULL,
    client_session character varying(36) NOT NULL
);


ALTER TABLE public.client_session_prot_mapper OWNER TO keycloak_user;

--
-- Name: client_session_role; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_session_role (
    role_id character varying(255) NOT NULL,
    client_session character varying(36) NOT NULL
);


ALTER TABLE public.client_session_role OWNER TO keycloak_user;

--
-- Name: client_user_session_note; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.client_user_session_note (
    name character varying(255) NOT NULL,
    value character varying(2048),
    client_session character varying(36) NOT NULL
);


ALTER TABLE public.client_user_session_note OWNER TO keycloak_user;

--
-- Name: component; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.component (
    id character varying(36) NOT NULL,
    name character varying(255),
    parent_id character varying(36),
    provider_id character varying(36),
    provider_type character varying(255),
    realm_id character varying(36),
    sub_type character varying(255)
);


ALTER TABLE public.component OWNER TO keycloak_user;

--
-- Name: component_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.component_config (
    id character varying(36) NOT NULL,
    component_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.component_config OWNER TO keycloak_user;

--
-- Name: composite_role; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.composite_role (
    composite character varying(36) NOT NULL,
    child_role character varying(36) NOT NULL
);


ALTER TABLE public.composite_role OWNER TO keycloak_user;

--
-- Name: credential; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.credential (
    id character varying(36) NOT NULL,
    salt bytea,
    type character varying(255),
    user_id character varying(36),
    created_date bigint,
    user_label character varying(255),
    secret_data text,
    credential_data text,
    priority integer
);


ALTER TABLE public.credential OWNER TO keycloak_user;

--
-- Name: databasechangelog; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.databasechangelog (
    id character varying(255) NOT NULL,
    author character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    dateexecuted timestamp without time zone NOT NULL,
    orderexecuted integer NOT NULL,
    exectype character varying(10) NOT NULL,
    md5sum character varying(35),
    description character varying(255),
    comments character varying(255),
    tag character varying(255),
    liquibase character varying(20),
    contexts character varying(255),
    labels character varying(255),
    deployment_id character varying(10)
);


ALTER TABLE public.databasechangelog OWNER TO keycloak_user;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE public.databasechangeloglock OWNER TO keycloak_user;

--
-- Name: default_client_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.default_client_scope (
    realm_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL,
    default_scope boolean DEFAULT false NOT NULL
);


ALTER TABLE public.default_client_scope OWNER TO keycloak_user;

--
-- Name: event_entity; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.event_entity (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    details_json character varying(2550),
    error character varying(255),
    ip_address character varying(255),
    realm_id character varying(255),
    session_id character varying(255),
    event_time bigint,
    type character varying(255),
    user_id character varying(255),
    details_json_long_value text
);


ALTER TABLE public.event_entity OWNER TO keycloak_user;

--
-- Name: fed_user_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_attribute (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    value character varying(2024),
    long_value_hash bytea,
    long_value_hash_lower_case bytea,
    long_value text
);


ALTER TABLE public.fed_user_attribute OWNER TO keycloak_user;

--
-- Name: fed_user_consent; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_consent (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    created_date bigint,
    last_updated_date bigint,
    client_storage_provider character varying(36),
    external_client_id character varying(255)
);


ALTER TABLE public.fed_user_consent OWNER TO keycloak_user;

--
-- Name: fed_user_consent_cl_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_consent_cl_scope (
    user_consent_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.fed_user_consent_cl_scope OWNER TO keycloak_user;

--
-- Name: fed_user_credential; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_credential (
    id character varying(36) NOT NULL,
    salt bytea,
    type character varying(255),
    created_date bigint,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    user_label character varying(255),
    secret_data text,
    credential_data text,
    priority integer
);


ALTER TABLE public.fed_user_credential OWNER TO keycloak_user;

--
-- Name: fed_user_group_membership; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_group_membership (
    group_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_group_membership OWNER TO keycloak_user;

--
-- Name: fed_user_required_action; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_required_action (
    required_action character varying(255) DEFAULT ' '::character varying NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_required_action OWNER TO keycloak_user;

--
-- Name: fed_user_role_mapping; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.fed_user_role_mapping (
    role_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_role_mapping OWNER TO keycloak_user;

--
-- Name: federated_identity; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.federated_identity (
    identity_provider character varying(255) NOT NULL,
    realm_id character varying(36),
    federated_user_id character varying(255),
    federated_username character varying(255),
    token text,
    user_id character varying(36) NOT NULL
);


ALTER TABLE public.federated_identity OWNER TO keycloak_user;

--
-- Name: federated_user; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.federated_user (
    id character varying(255) NOT NULL,
    storage_provider_id character varying(255),
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.federated_user OWNER TO keycloak_user;

--
-- Name: group_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.group_attribute (
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255),
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.group_attribute OWNER TO keycloak_user;

--
-- Name: group_role_mapping; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.group_role_mapping (
    role_id character varying(36) NOT NULL,
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.group_role_mapping OWNER TO keycloak_user;

--
-- Name: identity_provider; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.identity_provider (
    internal_id character varying(36) NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    provider_alias character varying(255),
    provider_id character varying(255),
    store_token boolean DEFAULT false NOT NULL,
    authenticate_by_default boolean DEFAULT false NOT NULL,
    realm_id character varying(36),
    add_token_role boolean DEFAULT true NOT NULL,
    trust_email boolean DEFAULT false NOT NULL,
    first_broker_login_flow_id character varying(36),
    post_broker_login_flow_id character varying(36),
    provider_display_name character varying(255),
    link_only boolean DEFAULT false NOT NULL
);


ALTER TABLE public.identity_provider OWNER TO keycloak_user;

--
-- Name: identity_provider_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.identity_provider_config (
    identity_provider_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.identity_provider_config OWNER TO keycloak_user;

--
-- Name: identity_provider_mapper; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.identity_provider_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    idp_alias character varying(255) NOT NULL,
    idp_mapper_name character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.identity_provider_mapper OWNER TO keycloak_user;

--
-- Name: idp_mapper_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.idp_mapper_config (
    idp_mapper_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.idp_mapper_config OWNER TO keycloak_user;

--
-- Name: keycloak_group; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.keycloak_group (
    id character varying(36) NOT NULL,
    name character varying(255),
    parent_group character varying(36) NOT NULL,
    realm_id character varying(36)
);


ALTER TABLE public.keycloak_group OWNER TO keycloak_user;

--
-- Name: keycloak_role; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.keycloak_role (
    id character varying(36) NOT NULL,
    client_realm_constraint character varying(255),
    client_role boolean DEFAULT false NOT NULL,
    description character varying(255),
    name character varying(255),
    realm_id character varying(255),
    client character varying(36),
    realm character varying(36)
);


ALTER TABLE public.keycloak_role OWNER TO keycloak_user;

--
-- Name: migration_model; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.migration_model (
    id character varying(36) NOT NULL,
    version character varying(36),
    update_time bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.migration_model OWNER TO keycloak_user;

--
-- Name: offline_client_session; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.offline_client_session (
    user_session_id character varying(36) NOT NULL,
    client_id character varying(255) NOT NULL,
    offline_flag character varying(4) NOT NULL,
    "timestamp" integer,
    data text,
    client_storage_provider character varying(36) DEFAULT 'local'::character varying NOT NULL,
    external_client_id character varying(255) DEFAULT 'local'::character varying NOT NULL,
    version integer DEFAULT 0
);


ALTER TABLE public.offline_client_session OWNER TO keycloak_user;

--
-- Name: offline_user_session; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.offline_user_session (
    user_session_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    created_on integer NOT NULL,
    offline_flag character varying(4) NOT NULL,
    data text,
    last_session_refresh integer DEFAULT 0 NOT NULL,
    broker_session_id character varying(1024),
    version integer DEFAULT 0
);


ALTER TABLE public.offline_user_session OWNER TO keycloak_user;

--
-- Name: org; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.org (
    id character varying(255) NOT NULL,
    enabled boolean NOT NULL,
    realm_id character varying(255) NOT NULL,
    group_id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(4000)
);


ALTER TABLE public.org OWNER TO keycloak_user;

--
-- Name: org_domain; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.org_domain (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    verified boolean NOT NULL,
    org_id character varying(255) NOT NULL
);


ALTER TABLE public.org_domain OWNER TO keycloak_user;

--
-- Name: policy_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.policy_config (
    policy_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.policy_config OWNER TO keycloak_user;

--
-- Name: protocol_mapper; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.protocol_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    protocol character varying(255) NOT NULL,
    protocol_mapper_name character varying(255) NOT NULL,
    client_id character varying(36),
    client_scope_id character varying(36)
);


ALTER TABLE public.protocol_mapper OWNER TO keycloak_user;

--
-- Name: protocol_mapper_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.protocol_mapper_config (
    protocol_mapper_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.protocol_mapper_config OWNER TO keycloak_user;

--
-- Name: realm; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm (
    id character varying(36) NOT NULL,
    access_code_lifespan integer,
    user_action_lifespan integer,
    access_token_lifespan integer,
    account_theme character varying(255),
    admin_theme character varying(255),
    email_theme character varying(255),
    enabled boolean DEFAULT false NOT NULL,
    events_enabled boolean DEFAULT false NOT NULL,
    events_expiration bigint,
    login_theme character varying(255),
    name character varying(255),
    not_before integer,
    password_policy character varying(2550),
    registration_allowed boolean DEFAULT false NOT NULL,
    remember_me boolean DEFAULT false NOT NULL,
    reset_password_allowed boolean DEFAULT false NOT NULL,
    social boolean DEFAULT false NOT NULL,
    ssl_required character varying(255),
    sso_idle_timeout integer,
    sso_max_lifespan integer,
    update_profile_on_soc_login boolean DEFAULT false NOT NULL,
    verify_email boolean DEFAULT false NOT NULL,
    master_admin_client character varying(36),
    login_lifespan integer,
    internationalization_enabled boolean DEFAULT false NOT NULL,
    default_locale character varying(255),
    reg_email_as_username boolean DEFAULT false NOT NULL,
    admin_events_enabled boolean DEFAULT false NOT NULL,
    admin_events_details_enabled boolean DEFAULT false NOT NULL,
    edit_username_allowed boolean DEFAULT false NOT NULL,
    otp_policy_counter integer DEFAULT 0,
    otp_policy_window integer DEFAULT 1,
    otp_policy_period integer DEFAULT 30,
    otp_policy_digits integer DEFAULT 6,
    otp_policy_alg character varying(36) DEFAULT 'HmacSHA1'::character varying,
    otp_policy_type character varying(36) DEFAULT 'totp'::character varying,
    browser_flow character varying(36),
    registration_flow character varying(36),
    direct_grant_flow character varying(36),
    reset_credentials_flow character varying(36),
    client_auth_flow character varying(36),
    offline_session_idle_timeout integer DEFAULT 0,
    revoke_refresh_token boolean DEFAULT false NOT NULL,
    access_token_life_implicit integer DEFAULT 0,
    login_with_email_allowed boolean DEFAULT true NOT NULL,
    duplicate_emails_allowed boolean DEFAULT false NOT NULL,
    docker_auth_flow character varying(36),
    refresh_token_max_reuse integer DEFAULT 0,
    allow_user_managed_access boolean DEFAULT false NOT NULL,
    sso_max_lifespan_remember_me integer DEFAULT 0 NOT NULL,
    sso_idle_timeout_remember_me integer DEFAULT 0 NOT NULL,
    default_role character varying(255)
);


ALTER TABLE public.realm OWNER TO keycloak_user;

--
-- Name: realm_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_attribute (
    name character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    value text
);


ALTER TABLE public.realm_attribute OWNER TO keycloak_user;

--
-- Name: realm_default_groups; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_default_groups (
    realm_id character varying(36) NOT NULL,
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.realm_default_groups OWNER TO keycloak_user;

--
-- Name: realm_enabled_event_types; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_enabled_event_types (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_enabled_event_types OWNER TO keycloak_user;

--
-- Name: realm_events_listeners; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_events_listeners (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_events_listeners OWNER TO keycloak_user;

--
-- Name: realm_localizations; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_localizations (
    realm_id character varying(255) NOT NULL,
    locale character varying(255) NOT NULL,
    texts text NOT NULL
);


ALTER TABLE public.realm_localizations OWNER TO keycloak_user;

--
-- Name: realm_required_credential; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_required_credential (
    type character varying(255) NOT NULL,
    form_label character varying(255),
    input boolean DEFAULT false NOT NULL,
    secret boolean DEFAULT false NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.realm_required_credential OWNER TO keycloak_user;

--
-- Name: realm_smtp_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_smtp_config (
    realm_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.realm_smtp_config OWNER TO keycloak_user;

--
-- Name: realm_supported_locales; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.realm_supported_locales (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_supported_locales OWNER TO keycloak_user;

--
-- Name: redirect_uris; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.redirect_uris (
    client_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.redirect_uris OWNER TO keycloak_user;

--
-- Name: required_action_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.required_action_config (
    required_action_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.required_action_config OWNER TO keycloak_user;

--
-- Name: required_action_provider; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.required_action_provider (
    id character varying(36) NOT NULL,
    alias character varying(255),
    name character varying(255),
    realm_id character varying(36),
    enabled boolean DEFAULT false NOT NULL,
    default_action boolean DEFAULT false NOT NULL,
    provider_id character varying(255),
    priority integer
);


ALTER TABLE public.required_action_provider OWNER TO keycloak_user;

--
-- Name: resource_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_attribute (
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255),
    resource_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_attribute OWNER TO keycloak_user;

--
-- Name: resource_policy; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_policy (
    resource_id character varying(36) NOT NULL,
    policy_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_policy OWNER TO keycloak_user;

--
-- Name: resource_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_scope (
    resource_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_scope OWNER TO keycloak_user;

--
-- Name: resource_server; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_server (
    id character varying(36) NOT NULL,
    allow_rs_remote_mgmt boolean DEFAULT false NOT NULL,
    policy_enforce_mode smallint NOT NULL,
    decision_strategy smallint DEFAULT 1 NOT NULL
);


ALTER TABLE public.resource_server OWNER TO keycloak_user;

--
-- Name: resource_server_perm_ticket; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_server_perm_ticket (
    id character varying(36) NOT NULL,
    owner character varying(255) NOT NULL,
    requester character varying(255) NOT NULL,
    created_timestamp bigint NOT NULL,
    granted_timestamp bigint,
    resource_id character varying(36) NOT NULL,
    scope_id character varying(36),
    resource_server_id character varying(36) NOT NULL,
    policy_id character varying(36)
);


ALTER TABLE public.resource_server_perm_ticket OWNER TO keycloak_user;

--
-- Name: resource_server_policy; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_server_policy (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255),
    type character varying(255) NOT NULL,
    decision_strategy smallint,
    logic smallint,
    resource_server_id character varying(36) NOT NULL,
    owner character varying(255)
);


ALTER TABLE public.resource_server_policy OWNER TO keycloak_user;

--
-- Name: resource_server_resource; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_server_resource (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(255),
    icon_uri character varying(255),
    owner character varying(255) NOT NULL,
    resource_server_id character varying(36) NOT NULL,
    owner_managed_access boolean DEFAULT false NOT NULL,
    display_name character varying(255)
);


ALTER TABLE public.resource_server_resource OWNER TO keycloak_user;

--
-- Name: resource_server_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_server_scope (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    icon_uri character varying(255),
    resource_server_id character varying(36) NOT NULL,
    display_name character varying(255)
);


ALTER TABLE public.resource_server_scope OWNER TO keycloak_user;

--
-- Name: resource_uris; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.resource_uris (
    resource_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.resource_uris OWNER TO keycloak_user;

--
-- Name: role_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.role_attribute (
    id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255)
);


ALTER TABLE public.role_attribute OWNER TO keycloak_user;

--
-- Name: scope_mapping; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.scope_mapping (
    client_id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL
);


ALTER TABLE public.scope_mapping OWNER TO keycloak_user;

--
-- Name: scope_policy; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.scope_policy (
    scope_id character varying(36) NOT NULL,
    policy_id character varying(36) NOT NULL
);


ALTER TABLE public.scope_policy OWNER TO keycloak_user;

--
-- Name: user_attribute; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_attribute (
    name character varying(255) NOT NULL,
    value character varying(255),
    user_id character varying(36) NOT NULL,
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    long_value_hash bytea,
    long_value_hash_lower_case bytea,
    long_value text
);


ALTER TABLE public.user_attribute OWNER TO keycloak_user;

--
-- Name: user_consent; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_consent (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    user_id character varying(36) NOT NULL,
    created_date bigint,
    last_updated_date bigint,
    client_storage_provider character varying(36),
    external_client_id character varying(255)
);


ALTER TABLE public.user_consent OWNER TO keycloak_user;

--
-- Name: user_consent_client_scope; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_consent_client_scope (
    user_consent_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.user_consent_client_scope OWNER TO keycloak_user;

--
-- Name: user_entity; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_entity (
    id character varying(36) NOT NULL,
    email character varying(255),
    email_constraint character varying(255),
    email_verified boolean DEFAULT false NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    federation_link character varying(255),
    first_name character varying(255),
    last_name character varying(255),
    realm_id character varying(255),
    username character varying(255),
    created_timestamp bigint,
    service_account_client_link character varying(255),
    not_before integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.user_entity OWNER TO keycloak_user;

--
-- Name: user_federation_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_federation_config (
    user_federation_provider_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.user_federation_config OWNER TO keycloak_user;

--
-- Name: user_federation_mapper; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_federation_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    federation_provider_id character varying(36) NOT NULL,
    federation_mapper_type character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.user_federation_mapper OWNER TO keycloak_user;

--
-- Name: user_federation_mapper_config; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_federation_mapper_config (
    user_federation_mapper_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.user_federation_mapper_config OWNER TO keycloak_user;

--
-- Name: user_federation_provider; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_federation_provider (
    id character varying(36) NOT NULL,
    changed_sync_period integer,
    display_name character varying(255),
    full_sync_period integer,
    last_sync integer,
    priority integer,
    provider_name character varying(255),
    realm_id character varying(36)
);


ALTER TABLE public.user_federation_provider OWNER TO keycloak_user;

--
-- Name: user_group_membership; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_group_membership (
    group_id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL
);


ALTER TABLE public.user_group_membership OWNER TO keycloak_user;

--
-- Name: user_required_action; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_required_action (
    user_id character varying(36) NOT NULL,
    required_action character varying(255) DEFAULT ' '::character varying NOT NULL
);


ALTER TABLE public.user_required_action OWNER TO keycloak_user;

--
-- Name: user_role_mapping; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_role_mapping (
    role_id character varying(255) NOT NULL,
    user_id character varying(36) NOT NULL
);


ALTER TABLE public.user_role_mapping OWNER TO keycloak_user;

--
-- Name: user_session; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_session (
    id character varying(36) NOT NULL,
    auth_method character varying(255),
    ip_address character varying(255),
    last_session_refresh integer,
    login_username character varying(255),
    realm_id character varying(255),
    remember_me boolean DEFAULT false NOT NULL,
    started integer,
    user_id character varying(255),
    user_session_state integer,
    broker_session_id character varying(255),
    broker_user_id character varying(255)
);


ALTER TABLE public.user_session OWNER TO keycloak_user;

--
-- Name: user_session_note; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.user_session_note (
    user_session character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(2048)
);


ALTER TABLE public.user_session_note OWNER TO keycloak_user;

--
-- Name: username_login_failure; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.username_login_failure (
    realm_id character varying(36) NOT NULL,
    username character varying(255) NOT NULL,
    failed_login_not_before integer,
    last_failure bigint,
    last_ip_failure character varying(255),
    num_failures integer
);


ALTER TABLE public.username_login_failure OWNER TO keycloak_user;

--
-- Name: web_origins; Type: TABLE; Schema: public; Owner: keycloak_user
--

CREATE TABLE public.web_origins (
    client_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.web_origins OWNER TO keycloak_user;

--
-- Data for Name: admin_event_entity; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.admin_event_entity (id, admin_event_time, realm_id, operation_type, auth_realm_id, auth_client_id, auth_user_id, ip_address, resource_path, representation, error, resource_type) FROM stdin;
\.


--
-- Data for Name: associated_policy; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.associated_policy (policy_id, associated_policy_id) FROM stdin;
\.


--
-- Data for Name: authentication_execution; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.authentication_execution (id, alias, authenticator, realm_id, flow_id, requirement, priority, authenticator_flow, auth_flow_id, auth_config) FROM stdin;
c8a47a00-f63f-48a3-9b85-826dc0495507	\N	auth-cookie	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	999b03f6-bc36-4d0d-86c6-f5770b4491e0	2	10	f	\N	\N
e0522d64-a18b-46bf-ad26-0f45ea2f4d83	\N	auth-spnego	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	999b03f6-bc36-4d0d-86c6-f5770b4491e0	3	20	f	\N	\N
3a319cce-9757-4aee-8ab9-db952cfd8519	\N	identity-provider-redirector	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	999b03f6-bc36-4d0d-86c6-f5770b4491e0	2	25	f	\N	\N
20b7494d-9e92-4f3c-a097-8fe702ae39a1	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	999b03f6-bc36-4d0d-86c6-f5770b4491e0	2	30	t	e04e3242-b4d9-41e5-a411-e3dcb09c3c8b	\N
093d91ed-1852-4288-9539-ea1e9546ff3c	\N	auth-username-password-form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	e04e3242-b4d9-41e5-a411-e3dcb09c3c8b	0	10	f	\N	\N
ba5dac52-9e62-4cf4-b940-166f866a8044	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	e04e3242-b4d9-41e5-a411-e3dcb09c3c8b	1	20	t	a3866206-3bca-4c8b-976e-17e618938fca	\N
55f2a266-344b-4160-808d-0f823ae7d04a	\N	conditional-user-configured	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	a3866206-3bca-4c8b-976e-17e618938fca	0	10	f	\N	\N
f2b39a2e-be89-46b0-83b9-fd044382df25	\N	auth-otp-form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	a3866206-3bca-4c8b-976e-17e618938fca	0	20	f	\N	\N
cb420efe-4eba-4bfa-b9cb-69f62777b667	\N	direct-grant-validate-username	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f6e06a1b-3eb4-4715-9d69-d39b0b661faa	0	10	f	\N	\N
440ea5af-68b0-474a-9653-f666d6c0be25	\N	direct-grant-validate-password	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f6e06a1b-3eb4-4715-9d69-d39b0b661faa	0	20	f	\N	\N
776e7d86-56be-40f4-9cec-23cde2313517	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f6e06a1b-3eb4-4715-9d69-d39b0b661faa	1	30	t	35a27608-3ab9-4753-8bf9-4f7b711898db	\N
05901e23-dd95-4585-b02c-30ac6cf3b21d	\N	conditional-user-configured	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	35a27608-3ab9-4753-8bf9-4f7b711898db	0	10	f	\N	\N
a4cbec69-a814-4804-b7a0-9a26bdad1c26	\N	direct-grant-validate-otp	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	35a27608-3ab9-4753-8bf9-4f7b711898db	0	20	f	\N	\N
14ce47dd-7547-4b48-a8b6-f42cd9562f59	\N	registration-page-form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	a836592f-06cc-4a7d-81c8-ca9cbefe27a4	0	10	t	673f6133-865c-45fd-b6d1-a34de7b346e2	\N
2a26c783-d0fd-4f7e-8c18-1fe1adc8ddd9	\N	registration-user-creation	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	673f6133-865c-45fd-b6d1-a34de7b346e2	0	20	f	\N	\N
18392333-0d0a-4522-bc4a-2868e6b40d9b	\N	registration-password-action	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	673f6133-865c-45fd-b6d1-a34de7b346e2	0	50	f	\N	\N
c43a6b0c-bebc-4088-82a8-82f39b7ca7e8	\N	registration-recaptcha-action	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	673f6133-865c-45fd-b6d1-a34de7b346e2	3	60	f	\N	\N
f41847f4-29a7-463b-b20e-6f2b151fa94a	\N	registration-terms-and-conditions	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	673f6133-865c-45fd-b6d1-a34de7b346e2	3	70	f	\N	\N
6963c1ae-4a49-4de7-98c0-d516bbdc2882	\N	reset-credentials-choose-user	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3d65f07f-1929-4bc5-9f25-fd2dfe675142	0	10	f	\N	\N
7432a002-3553-464f-9557-a00eec0a4bf8	\N	reset-credential-email	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3d65f07f-1929-4bc5-9f25-fd2dfe675142	0	20	f	\N	\N
c11a726a-6dcb-4c93-80a9-9b01ebe95907	\N	reset-password	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3d65f07f-1929-4bc5-9f25-fd2dfe675142	0	30	f	\N	\N
83c1e87a-1933-460d-b656-a568fcb94595	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3d65f07f-1929-4bc5-9f25-fd2dfe675142	1	40	t	523ef631-812b-4b4f-b29b-1a80ab410c2c	\N
5f6f23cf-abfd-4968-92ba-b3c14b6ecc86	\N	conditional-user-configured	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	523ef631-812b-4b4f-b29b-1a80ab410c2c	0	10	f	\N	\N
f863ef2e-fd68-452c-a59d-8bfb6bac89ca	\N	reset-otp	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	523ef631-812b-4b4f-b29b-1a80ab410c2c	0	20	f	\N	\N
9a1c2277-c43c-47a3-96ad-9f0d07b56df0	\N	client-secret	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	4ee9f7ca-86ad-4489-b866-392c6c62caa1	2	10	f	\N	\N
19f0d268-ab90-4fa2-98d6-13711b52979a	\N	client-jwt	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	4ee9f7ca-86ad-4489-b866-392c6c62caa1	2	20	f	\N	\N
cedba3ad-6f24-4e74-8937-76d3cd281862	\N	client-secret-jwt	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	4ee9f7ca-86ad-4489-b866-392c6c62caa1	2	30	f	\N	\N
eaefc3fd-ec38-4b00-a7c5-2fff8228ba72	\N	client-x509	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	4ee9f7ca-86ad-4489-b866-392c6c62caa1	2	40	f	\N	\N
ed9198af-ff7d-4156-93e7-bb9394137bc6	\N	idp-review-profile	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	988f94e6-631a-4993-ad60-528952242c61	0	10	f	\N	8d217f34-9899-4072-bb2d-003222c4960b
91846b33-7c76-4363-b37c-6f371a0d43f9	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	988f94e6-631a-4993-ad60-528952242c61	0	20	t	fe55e13a-6fc7-46d7-97e7-33b565d02ef2	\N
52c4bd5f-9ca7-4040-974b-d8b80d9f9b2a	\N	idp-create-user-if-unique	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	fe55e13a-6fc7-46d7-97e7-33b565d02ef2	2	10	f	\N	2d22d032-ee1f-43b3-b7a2-ecb0b6dec846
5994628a-9bd3-4854-a865-a15902fd3de4	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	fe55e13a-6fc7-46d7-97e7-33b565d02ef2	2	20	t	31f97ccb-20a1-4a11-aa45-58577e097b06	\N
0383a9fe-82b0-4712-b204-a6d7962b2920	\N	idp-confirm-link	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	31f97ccb-20a1-4a11-aa45-58577e097b06	0	10	f	\N	\N
daa00039-232d-4d0d-9be3-a6f20c8ace17	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	31f97ccb-20a1-4a11-aa45-58577e097b06	0	20	t	3ff89d91-a014-4125-9302-e03e304cd688	\N
fe1b3d23-235d-4b47-bab9-e4971927ae22	\N	idp-email-verification	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3ff89d91-a014-4125-9302-e03e304cd688	2	10	f	\N	\N
564f2085-11e3-4f58-9d5e-10ae93d824d1	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3ff89d91-a014-4125-9302-e03e304cd688	2	20	t	ae79985a-c8f4-4d96-9e86-3532fa7b8973	\N
7920fa8f-2dba-4952-aa24-61a49392f8e0	\N	idp-username-password-form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	ae79985a-c8f4-4d96-9e86-3532fa7b8973	0	10	f	\N	\N
3c3897cc-b92c-4cfc-8a66-82f7c18aa280	\N	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	ae79985a-c8f4-4d96-9e86-3532fa7b8973	1	20	t	2f2fb05b-ad16-4a93-a590-96107923b07f	\N
f381fccd-e570-478d-8a59-7e7495f3ad66	\N	conditional-user-configured	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	2f2fb05b-ad16-4a93-a590-96107923b07f	0	10	f	\N	\N
6a029957-ef06-4b8c-876d-a5f3e912c7d9	\N	auth-otp-form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	2f2fb05b-ad16-4a93-a590-96107923b07f	0	20	f	\N	\N
f9249b42-729b-43c8-a2a1-534182ff9eb9	\N	http-basic-authenticator	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	bf815317-2b73-4053-8133-b7ec19092979	0	10	f	\N	\N
014a672d-2b47-4b6a-9f6f-5d232f609729	\N	docker-http-basic-authenticator	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	4c7e065b-0f1d-41d7-845c-3afed6616336	0	10	f	\N	\N
f970deba-3e4c-4d48-8943-621fb05d7d81	\N	auth-cookie	6a264182-ab2b-4da7-a868-c7dddf4329f2	a2587804-176c-450d-9be8-0744f47249ab	2	10	f	\N	\N
905b99a7-55d1-486a-9df4-661db1661293	\N	auth-spnego	6a264182-ab2b-4da7-a868-c7dddf4329f2	a2587804-176c-450d-9be8-0744f47249ab	3	20	f	\N	\N
3ebc2571-163d-4d2e-9434-fe43d5b2a2be	\N	identity-provider-redirector	6a264182-ab2b-4da7-a868-c7dddf4329f2	a2587804-176c-450d-9be8-0744f47249ab	2	25	f	\N	\N
95ef00ea-6abf-40f3-b31f-fef48d993895	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	a2587804-176c-450d-9be8-0744f47249ab	2	30	t	bb2142be-2282-4b44-b717-4f0da7cca534	\N
48f0a8fb-9d32-4a75-bb6e-f10e84d5df19	\N	auth-username-password-form	6a264182-ab2b-4da7-a868-c7dddf4329f2	bb2142be-2282-4b44-b717-4f0da7cca534	0	10	f	\N	\N
e37510ae-35cd-48ec-b62c-7f12e93cefc0	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	bb2142be-2282-4b44-b717-4f0da7cca534	1	20	t	6f689a3e-bb2e-4450-a0d5-6e8a3626e388	\N
262ec63f-0969-4bfa-8c08-03ceed1bb1e9	\N	conditional-user-configured	6a264182-ab2b-4da7-a868-c7dddf4329f2	6f689a3e-bb2e-4450-a0d5-6e8a3626e388	0	10	f	\N	\N
92d04fc9-9c07-4b65-af19-0f7a86ac32ed	\N	auth-otp-form	6a264182-ab2b-4da7-a868-c7dddf4329f2	6f689a3e-bb2e-4450-a0d5-6e8a3626e388	0	20	f	\N	\N
ae5a1368-6894-47bf-9dd5-f9c5ace3e470	\N	direct-grant-validate-username	6a264182-ab2b-4da7-a868-c7dddf4329f2	6e9428d2-d658-43f7-97c6-315bf26de400	0	10	f	\N	\N
f8b24c4e-b076-4138-999d-23f94e544645	\N	direct-grant-validate-password	6a264182-ab2b-4da7-a868-c7dddf4329f2	6e9428d2-d658-43f7-97c6-315bf26de400	0	20	f	\N	\N
26205522-afc1-472b-848e-ed1804a8115c	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	6e9428d2-d658-43f7-97c6-315bf26de400	1	30	t	00dfc9a0-5f47-4dcf-8e18-2f10208f43c3	\N
b76a30e1-de73-406a-b5ea-7d05719143e6	\N	conditional-user-configured	6a264182-ab2b-4da7-a868-c7dddf4329f2	00dfc9a0-5f47-4dcf-8e18-2f10208f43c3	0	10	f	\N	\N
4b2c9011-4f96-4750-ab8c-e1fe25efab8f	\N	direct-grant-validate-otp	6a264182-ab2b-4da7-a868-c7dddf4329f2	00dfc9a0-5f47-4dcf-8e18-2f10208f43c3	0	20	f	\N	\N
f337e885-b631-4f8d-b8f2-c94b9f94bf7c	\N	registration-page-form	6a264182-ab2b-4da7-a868-c7dddf4329f2	92d62f3e-ada7-4f9e-9454-a9921fa2918c	0	10	t	47b40258-034d-4985-b615-e9dd4fe25b17	\N
3797ba4b-758b-47cc-8df1-892c30ffc151	\N	registration-user-creation	6a264182-ab2b-4da7-a868-c7dddf4329f2	47b40258-034d-4985-b615-e9dd4fe25b17	0	20	f	\N	\N
8acc989c-b591-401d-ab40-512acdefa29e	\N	registration-password-action	6a264182-ab2b-4da7-a868-c7dddf4329f2	47b40258-034d-4985-b615-e9dd4fe25b17	0	50	f	\N	\N
ffdb4185-663a-4267-9323-30ac40ecc0cc	\N	registration-recaptcha-action	6a264182-ab2b-4da7-a868-c7dddf4329f2	47b40258-034d-4985-b615-e9dd4fe25b17	3	60	f	\N	\N
03117398-4175-4c8b-a396-4482ba6a69b7	\N	registration-terms-and-conditions	6a264182-ab2b-4da7-a868-c7dddf4329f2	47b40258-034d-4985-b615-e9dd4fe25b17	3	70	f	\N	\N
639f834d-52b0-483a-8658-fe3c52bfb8b3	\N	reset-credentials-choose-user	6a264182-ab2b-4da7-a868-c7dddf4329f2	640f6c14-8515-407e-8928-4729fa870ea4	0	10	f	\N	\N
d6680782-34a9-4ec4-a6a7-ef8fd58bfe3d	\N	reset-credential-email	6a264182-ab2b-4da7-a868-c7dddf4329f2	640f6c14-8515-407e-8928-4729fa870ea4	0	20	f	\N	\N
b1da4e02-1002-44b2-bc0a-c3ed11c585f2	\N	reset-password	6a264182-ab2b-4da7-a868-c7dddf4329f2	640f6c14-8515-407e-8928-4729fa870ea4	0	30	f	\N	\N
b409d855-bc54-4e7c-9ee6-dcfedb073a10	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	640f6c14-8515-407e-8928-4729fa870ea4	1	40	t	f1535c16-d1b1-46a1-8526-3a587b0c3481	\N
db7df8d5-31d9-41d7-8a5a-2b85c159cb55	\N	conditional-user-configured	6a264182-ab2b-4da7-a868-c7dddf4329f2	f1535c16-d1b1-46a1-8526-3a587b0c3481	0	10	f	\N	\N
5637e1f0-5952-4a29-bf67-1ba678558a4c	\N	reset-otp	6a264182-ab2b-4da7-a868-c7dddf4329f2	f1535c16-d1b1-46a1-8526-3a587b0c3481	0	20	f	\N	\N
6f817766-5ee3-4495-8654-fbd4674d73aa	\N	client-secret	6a264182-ab2b-4da7-a868-c7dddf4329f2	d799aeff-0c88-416b-a0b7-c405d98330a1	2	10	f	\N	\N
9ee6686e-1a83-432e-a757-9a0b6609ffac	\N	client-jwt	6a264182-ab2b-4da7-a868-c7dddf4329f2	d799aeff-0c88-416b-a0b7-c405d98330a1	2	20	f	\N	\N
0ba2739e-3965-46f9-a7ec-735e642adb04	\N	client-secret-jwt	6a264182-ab2b-4da7-a868-c7dddf4329f2	d799aeff-0c88-416b-a0b7-c405d98330a1	2	30	f	\N	\N
af637260-5018-4526-808e-f1fe9d91a52c	\N	client-x509	6a264182-ab2b-4da7-a868-c7dddf4329f2	d799aeff-0c88-416b-a0b7-c405d98330a1	2	40	f	\N	\N
2e6ca478-336b-4f9f-ba97-625fc7bb6a72	\N	idp-review-profile	6a264182-ab2b-4da7-a868-c7dddf4329f2	38bbbaea-251b-4915-978f-90c3fb1a26cb	0	10	f	\N	9a8c0351-1fbd-4222-b3ab-22dd6775d171
a80608e1-483e-4028-8717-05640caace4e	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	38bbbaea-251b-4915-978f-90c3fb1a26cb	0	20	t	8cbd82c5-ff1a-4497-baa4-52946707bfe9	\N
8d98820c-a421-4019-bd22-76b8ddb9e67a	\N	idp-create-user-if-unique	6a264182-ab2b-4da7-a868-c7dddf4329f2	8cbd82c5-ff1a-4497-baa4-52946707bfe9	2	10	f	\N	9a5447a6-b952-45d6-8fd2-955442bdda96
ebcb44a5-a068-40c9-881a-62949e62caa8	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	8cbd82c5-ff1a-4497-baa4-52946707bfe9	2	20	t	32737384-fa85-4d89-8a28-336a53205a28	\N
f5b07d47-0c45-413a-aa20-8c6094708a78	\N	idp-confirm-link	6a264182-ab2b-4da7-a868-c7dddf4329f2	32737384-fa85-4d89-8a28-336a53205a28	0	10	f	\N	\N
945389d0-0538-4635-a29b-b2d31ee1edca	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	32737384-fa85-4d89-8a28-336a53205a28	0	20	t	0d3b84d4-5fd0-4f86-8ea6-a10344b6bc76	\N
718f502c-a343-4372-b248-1794493abd3c	\N	idp-email-verification	6a264182-ab2b-4da7-a868-c7dddf4329f2	0d3b84d4-5fd0-4f86-8ea6-a10344b6bc76	2	10	f	\N	\N
8c6bf295-9d48-4fda-911b-f3655d79e5b1	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	0d3b84d4-5fd0-4f86-8ea6-a10344b6bc76	2	20	t	3f844630-7916-4d34-a6ca-c1585a57ac7f	\N
317fa9e9-bed7-48fe-8030-586f5383f74e	\N	idp-username-password-form	6a264182-ab2b-4da7-a868-c7dddf4329f2	3f844630-7916-4d34-a6ca-c1585a57ac7f	0	10	f	\N	\N
4fb7a04f-28a5-4193-8b51-d39c7a7ca6ab	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	3f844630-7916-4d34-a6ca-c1585a57ac7f	1	20	t	01a08ca5-77b8-4d2f-b7bd-5d5833ad737e	\N
e2e235f2-5f69-4596-b294-7616b68c981e	\N	conditional-user-configured	6a264182-ab2b-4da7-a868-c7dddf4329f2	01a08ca5-77b8-4d2f-b7bd-5d5833ad737e	0	10	f	\N	\N
2c8b0902-b6c7-4ad8-9832-e396a82075ea	\N	auth-otp-form	6a264182-ab2b-4da7-a868-c7dddf4329f2	01a08ca5-77b8-4d2f-b7bd-5d5833ad737e	0	20	f	\N	\N
b0cae5ac-9945-43c3-a526-a79f8eadbed5	\N	http-basic-authenticator	6a264182-ab2b-4da7-a868-c7dddf4329f2	05a2ae73-5149-4541-9fbf-f51feb53e5d0	0	10	f	\N	\N
984c38af-0f39-4829-9418-0020582a16c3	\N	docker-http-basic-authenticator	6a264182-ab2b-4da7-a868-c7dddf4329f2	a7cd6873-6e89-4138-bb20-2e6fdf8c3b40	0	10	f	\N	\N
\.


--
-- Data for Name: authentication_flow; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.authentication_flow (id, alias, description, realm_id, provider_id, top_level, built_in) FROM stdin;
999b03f6-bc36-4d0d-86c6-f5770b4491e0	browser	browser based authentication	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
e04e3242-b4d9-41e5-a411-e3dcb09c3c8b	forms	Username, password, otp and other auth forms.	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
a3866206-3bca-4c8b-976e-17e618938fca	Browser - Conditional OTP	Flow to determine if the OTP is required for the authentication	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
f6e06a1b-3eb4-4715-9d69-d39b0b661faa	direct grant	OpenID Connect Resource Owner Grant	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
35a27608-3ab9-4753-8bf9-4f7b711898db	Direct Grant - Conditional OTP	Flow to determine if the OTP is required for the authentication	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
a836592f-06cc-4a7d-81c8-ca9cbefe27a4	registration	registration flow	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
673f6133-865c-45fd-b6d1-a34de7b346e2	registration form	registration form	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	form-flow	f	t
3d65f07f-1929-4bc5-9f25-fd2dfe675142	reset credentials	Reset credentials for a user if they forgot their password or something	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
523ef631-812b-4b4f-b29b-1a80ab410c2c	Reset - Conditional OTP	Flow to determine if the OTP should be reset or not. Set to REQUIRED to force.	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
4ee9f7ca-86ad-4489-b866-392c6c62caa1	clients	Base authentication for clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	client-flow	t	t
988f94e6-631a-4993-ad60-528952242c61	first broker login	Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
fe55e13a-6fc7-46d7-97e7-33b565d02ef2	User creation or linking	Flow for the existing/non-existing user alternatives	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
31f97ccb-20a1-4a11-aa45-58577e097b06	Handle Existing Account	Handle what to do if there is existing account with same email/username like authenticated identity provider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
3ff89d91-a014-4125-9302-e03e304cd688	Account verification options	Method with which to verity the existing account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
ae79985a-c8f4-4d96-9e86-3532fa7b8973	Verify Existing Account by Re-authentication	Reauthentication of existing account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
2f2fb05b-ad16-4a93-a590-96107923b07f	First broker login - Conditional OTP	Flow to determine if the OTP is required for the authentication	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	f	t
bf815317-2b73-4053-8133-b7ec19092979	saml ecp	SAML ECP Profile Authentication Flow	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
4c7e065b-0f1d-41d7-845c-3afed6616336	docker auth	Used by Docker clients to authenticate against the IDP	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	basic-flow	t	t
a2587804-176c-450d-9be8-0744f47249ab	browser	browser based authentication	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
bb2142be-2282-4b44-b717-4f0da7cca534	forms	Username, password, otp and other auth forms.	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
6f689a3e-bb2e-4450-a0d5-6e8a3626e388	Browser - Conditional OTP	Flow to determine if the OTP is required for the authentication	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
6e9428d2-d658-43f7-97c6-315bf26de400	direct grant	OpenID Connect Resource Owner Grant	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
00dfc9a0-5f47-4dcf-8e18-2f10208f43c3	Direct Grant - Conditional OTP	Flow to determine if the OTP is required for the authentication	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
92d62f3e-ada7-4f9e-9454-a9921fa2918c	registration	registration flow	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
47b40258-034d-4985-b615-e9dd4fe25b17	registration form	registration form	6a264182-ab2b-4da7-a868-c7dddf4329f2	form-flow	f	t
640f6c14-8515-407e-8928-4729fa870ea4	reset credentials	Reset credentials for a user if they forgot their password or something	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
f1535c16-d1b1-46a1-8526-3a587b0c3481	Reset - Conditional OTP	Flow to determine if the OTP should be reset or not. Set to REQUIRED to force.	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
d799aeff-0c88-416b-a0b7-c405d98330a1	clients	Base authentication for clients	6a264182-ab2b-4da7-a868-c7dddf4329f2	client-flow	t	t
38bbbaea-251b-4915-978f-90c3fb1a26cb	first broker login	Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
8cbd82c5-ff1a-4497-baa4-52946707bfe9	User creation or linking	Flow for the existing/non-existing user alternatives	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
32737384-fa85-4d89-8a28-336a53205a28	Handle Existing Account	Handle what to do if there is existing account with same email/username like authenticated identity provider	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
0d3b84d4-5fd0-4f86-8ea6-a10344b6bc76	Account verification options	Method with which to verity the existing account	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
3f844630-7916-4d34-a6ca-c1585a57ac7f	Verify Existing Account by Re-authentication	Reauthentication of existing account	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
01a08ca5-77b8-4d2f-b7bd-5d5833ad737e	First broker login - Conditional OTP	Flow to determine if the OTP is required for the authentication	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	f	t
05a2ae73-5149-4541-9fbf-f51feb53e5d0	saml ecp	SAML ECP Profile Authentication Flow	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
a7cd6873-6e89-4138-bb20-2e6fdf8c3b40	docker auth	Used by Docker clients to authenticate against the IDP	6a264182-ab2b-4da7-a868-c7dddf4329f2	basic-flow	t	t
\.


--
-- Data for Name: authenticator_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.authenticator_config (id, alias, realm_id) FROM stdin;
8d217f34-9899-4072-bb2d-003222c4960b	review profile config	1aecbfb5-44bb-49c8-a2ef-ef77293e300d
2d22d032-ee1f-43b3-b7a2-ecb0b6dec846	create unique user config	1aecbfb5-44bb-49c8-a2ef-ef77293e300d
9a8c0351-1fbd-4222-b3ab-22dd6775d171	review profile config	6a264182-ab2b-4da7-a868-c7dddf4329f2
9a5447a6-b952-45d6-8fd2-955442bdda96	create unique user config	6a264182-ab2b-4da7-a868-c7dddf4329f2
\.


--
-- Data for Name: authenticator_config_entry; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.authenticator_config_entry (authenticator_id, value, name) FROM stdin;
2d22d032-ee1f-43b3-b7a2-ecb0b6dec846	false	require.password.update.after.registration
8d217f34-9899-4072-bb2d-003222c4960b	missing	update.profile.on.first.login
9a5447a6-b952-45d6-8fd2-955442bdda96	false	require.password.update.after.registration
9a8c0351-1fbd-4222-b3ab-22dd6775d171	missing	update.profile.on.first.login
\.


--
-- Data for Name: broker_link; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.broker_link (identity_provider, storage_provider_id, realm_id, broker_user_id, broker_username, token, user_id) FROM stdin;
\.


--
-- Data for Name: client; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client (id, enabled, full_scope_allowed, client_id, not_before, public_client, secret, base_url, bearer_only, management_url, surrogate_auth_required, realm_id, protocol, node_rereg_timeout, frontchannel_logout, consent_required, name, service_accounts_enabled, client_authenticator_type, root_url, description, registration_token, standard_flow_enabled, implicit_flow_enabled, direct_access_grants_enabled, always_display_in_console) FROM stdin;
25a276e3-07eb-49e9-86a9-5a15a5f09800	t	f	master-realm	0	f	\N	\N	t	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	0	f	f	master Realm	f	client-secret	\N	\N	\N	t	f	f	f
28a13f19-a581-48cf-9d27-203c80b5be3a	t	f	account	0	t	\N	/realms/master/account/	f	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	openid-connect	0	f	f	${client_account}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	t	f	account-console	0	t	\N	/realms/master/account/	f	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	openid-connect	0	f	f	${client_account-console}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	t	f	broker	0	f	\N	\N	t	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	openid-connect	0	f	f	${client_broker}	f	client-secret	\N	\N	\N	t	f	f	f
c9127146-5188-4383-bc83-8371c445ed88	t	f	security-admin-console	0	t	\N	/admin/master/console/	f	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	openid-connect	0	f	f	${client_security-admin-console}	f	client-secret	${authAdminUrl}	\N	\N	t	f	f	f
dbc511ea-0fcb-482e-ad99-f94b603da0a8	t	f	admin-cli	0	t	\N	\N	f	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	openid-connect	0	f	f	${client_admin-cli}	f	client-secret	\N	\N	\N	f	f	t	f
724428c1-ccb1-4367-87f8-64d2d37295e8	t	f	pulse-realm	0	f	\N	\N	t	\N	f	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	0	f	f	pulse Realm	f	client-secret	\N	\N	\N	t	f	f	f
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	f	realm-management	0	f	\N	\N	t	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_realm-management}	f	client-secret	\N	\N	\N	t	f	f	f
6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	f	account	0	t	\N	/realms/pulse/account/	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_account}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
d2e77719-c7fa-48e1-9d93-95b5f409862a	t	f	account-console	0	t	\N	/realms/pulse/account/	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_account-console}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
3c612010-d61f-4061-adb1-a09a4b7c2a51	t	f	broker	0	f	\N	\N	t	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_broker}	f	client-secret	\N	\N	\N	t	f	f	f
94b40267-f844-4f8e-996e-3bc5b0800c08	t	f	security-admin-console	0	t	\N	/admin/pulse/console/	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_security-admin-console}	f	client-secret	${authAdminUrl}	\N	\N	t	f	f	f
809440f4-80ef-45a3-be47-4b824e521f2c	t	f	admin-cli	0	t	\N	\N	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	0	f	f	${client_admin-cli}	f	client-secret	\N	\N	\N	f	f	t	f
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	t	t	pulse-web	0	t	\N	\N	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	-1	f	f	Pulse RH Web	f	client-secret	\N	\N	\N	t	f	f	f
710ee357-9495-4b0b-8f44-907835d002b3	t	t	pulse-backend	0	f	PulseRH_BackendSecret_2026!	\N	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	-1	f	f	Pulse RH Backend	t	client-secret	\N	\N	\N	f	f	f	f
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	t	t	prometheus	0	f	PulseRH_PrometheusSecret_2026!	\N	f	\N	f	6a264182-ab2b-4da7-a868-c7dddf4329f2	openid-connect	-1	f	f	Prometheus	f	client-secret	\N	\N	\N	t	f	f	f
\.


--
-- Data for Name: client_attributes; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_attributes (client_id, name, value) FROM stdin;
28a13f19-a581-48cf-9d27-203c80b5be3a	post.logout.redirect.uris	+
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	post.logout.redirect.uris	+
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	pkce.code.challenge.method	S256
c9127146-5188-4383-bc83-8371c445ed88	post.logout.redirect.uris	+
c9127146-5188-4383-bc83-8371c445ed88	pkce.code.challenge.method	S256
6d6f00fd-79c0-4acc-a3de-b28063ec0926	post.logout.redirect.uris	+
d2e77719-c7fa-48e1-9d93-95b5f409862a	post.logout.redirect.uris	+
d2e77719-c7fa-48e1-9d93-95b5f409862a	pkce.code.challenge.method	S256
94b40267-f844-4f8e-996e-3bc5b0800c08	post.logout.redirect.uris	+
94b40267-f844-4f8e-996e-3bc5b0800c08	pkce.code.challenge.method	S256
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	post.logout.redirect.uris	+
710ee357-9495-4b0b-8f44-907835d002b3	post.logout.redirect.uris	+
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	post.logout.redirect.uris	+
\.


--
-- Data for Name: client_auth_flow_bindings; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_auth_flow_bindings (client_id, flow_id, binding_name) FROM stdin;
\.


--
-- Data for Name: client_initial_access; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_initial_access (id, realm_id, "timestamp", expiration, count, remaining_count) FROM stdin;
\.


--
-- Data for Name: client_node_registrations; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_node_registrations (client_id, value, name) FROM stdin;
\.


--
-- Data for Name: client_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_scope (id, name, realm_id, description, protocol) FROM stdin;
e7de7027-5f94-4eea-a86e-1b709749eb45	offline_access	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect built-in scope: offline_access	openid-connect
d0eb9230-68b8-4071-869b-377240dbde1f	role_list	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	SAML role list	saml
3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	profile	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect built-in scope: profile	openid-connect
fa3301c7-ea7f-4983-a85e-999570232089	email	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect built-in scope: email	openid-connect
37310c78-d1fd-4cfe-82b4-e94501f869e2	address	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect built-in scope: address	openid-connect
dff4c9c5-910a-4f48-ab2f-9819daddeba7	phone	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect built-in scope: phone	openid-connect
0fe1ad1b-d18e-47af-ae41-84830d69a087	roles	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect scope for add user roles to the access token	openid-connect
6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	web-origins	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect scope for add allowed web origins to the access token	openid-connect
b996718d-07af-4a21-a55f-4725e56f65d6	microprofile-jwt	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	Microprofile - JWT built-in scope	openid-connect
cffaa3e2-535b-4f21-aea4-acfe9a01727f	acr	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect scope for add acr (authentication context class reference) to the token	openid-connect
376ff0c4-cf97-4d39-bcfb-b3c20e837898	basic	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	OpenID Connect scope for add all basic claims to the token	openid-connect
05563931-429a-4f06-8e68-5dca524f810f	offline_access	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect built-in scope: offline_access	openid-connect
bcffc1cd-2dd6-4a6d-9b98-9adddf1990d2	role_list	6a264182-ab2b-4da7-a868-c7dddf4329f2	SAML role list	saml
9909b566-87fd-4c63-a73d-9bdbd519d20f	profile	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect built-in scope: profile	openid-connect
b6128b6c-a696-4741-ae21-17d2141078a2	email	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect built-in scope: email	openid-connect
f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	address	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect built-in scope: address	openid-connect
bb96564a-5296-4a0b-973c-d7d57122fa10	phone	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect built-in scope: phone	openid-connect
214d076c-cb63-47fd-867b-0686d3bea7bd	roles	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect scope for add user roles to the access token	openid-connect
9cbc56ff-df36-4b4b-884d-e98732737867	web-origins	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect scope for add allowed web origins to the access token	openid-connect
8fa29864-971f-4c81-9d21-12aaea3be7dd	microprofile-jwt	6a264182-ab2b-4da7-a868-c7dddf4329f2	Microprofile - JWT built-in scope	openid-connect
fb3d66d0-362f-4feb-a772-3c8a81766f8c	acr	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect scope for add acr (authentication context class reference) to the token	openid-connect
ba724387-db2e-430a-879b-6ec46f406df2	basic	6a264182-ab2b-4da7-a868-c7dddf4329f2	OpenID Connect scope for add all basic claims to the token	openid-connect
\.


--
-- Data for Name: client_scope_attributes; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_scope_attributes (scope_id, value, name) FROM stdin;
e7de7027-5f94-4eea-a86e-1b709749eb45	true	display.on.consent.screen
e7de7027-5f94-4eea-a86e-1b709749eb45	${offlineAccessScopeConsentText}	consent.screen.text
d0eb9230-68b8-4071-869b-377240dbde1f	true	display.on.consent.screen
d0eb9230-68b8-4071-869b-377240dbde1f	${samlRoleListScopeConsentText}	consent.screen.text
3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	true	display.on.consent.screen
3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	${profileScopeConsentText}	consent.screen.text
3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	true	include.in.token.scope
fa3301c7-ea7f-4983-a85e-999570232089	true	display.on.consent.screen
fa3301c7-ea7f-4983-a85e-999570232089	${emailScopeConsentText}	consent.screen.text
fa3301c7-ea7f-4983-a85e-999570232089	true	include.in.token.scope
37310c78-d1fd-4cfe-82b4-e94501f869e2	true	display.on.consent.screen
37310c78-d1fd-4cfe-82b4-e94501f869e2	${addressScopeConsentText}	consent.screen.text
37310c78-d1fd-4cfe-82b4-e94501f869e2	true	include.in.token.scope
dff4c9c5-910a-4f48-ab2f-9819daddeba7	true	display.on.consent.screen
dff4c9c5-910a-4f48-ab2f-9819daddeba7	${phoneScopeConsentText}	consent.screen.text
dff4c9c5-910a-4f48-ab2f-9819daddeba7	true	include.in.token.scope
0fe1ad1b-d18e-47af-ae41-84830d69a087	true	display.on.consent.screen
0fe1ad1b-d18e-47af-ae41-84830d69a087	${rolesScopeConsentText}	consent.screen.text
0fe1ad1b-d18e-47af-ae41-84830d69a087	false	include.in.token.scope
6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	false	display.on.consent.screen
6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf		consent.screen.text
6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	false	include.in.token.scope
b996718d-07af-4a21-a55f-4725e56f65d6	false	display.on.consent.screen
b996718d-07af-4a21-a55f-4725e56f65d6	true	include.in.token.scope
cffaa3e2-535b-4f21-aea4-acfe9a01727f	false	display.on.consent.screen
cffaa3e2-535b-4f21-aea4-acfe9a01727f	false	include.in.token.scope
376ff0c4-cf97-4d39-bcfb-b3c20e837898	false	display.on.consent.screen
376ff0c4-cf97-4d39-bcfb-b3c20e837898	false	include.in.token.scope
05563931-429a-4f06-8e68-5dca524f810f	true	display.on.consent.screen
05563931-429a-4f06-8e68-5dca524f810f	${offlineAccessScopeConsentText}	consent.screen.text
bcffc1cd-2dd6-4a6d-9b98-9adddf1990d2	true	display.on.consent.screen
bcffc1cd-2dd6-4a6d-9b98-9adddf1990d2	${samlRoleListScopeConsentText}	consent.screen.text
9909b566-87fd-4c63-a73d-9bdbd519d20f	true	display.on.consent.screen
9909b566-87fd-4c63-a73d-9bdbd519d20f	${profileScopeConsentText}	consent.screen.text
9909b566-87fd-4c63-a73d-9bdbd519d20f	true	include.in.token.scope
b6128b6c-a696-4741-ae21-17d2141078a2	true	display.on.consent.screen
b6128b6c-a696-4741-ae21-17d2141078a2	${emailScopeConsentText}	consent.screen.text
b6128b6c-a696-4741-ae21-17d2141078a2	true	include.in.token.scope
f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	true	display.on.consent.screen
f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	${addressScopeConsentText}	consent.screen.text
f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	true	include.in.token.scope
bb96564a-5296-4a0b-973c-d7d57122fa10	true	display.on.consent.screen
bb96564a-5296-4a0b-973c-d7d57122fa10	${phoneScopeConsentText}	consent.screen.text
bb96564a-5296-4a0b-973c-d7d57122fa10	true	include.in.token.scope
214d076c-cb63-47fd-867b-0686d3bea7bd	true	display.on.consent.screen
214d076c-cb63-47fd-867b-0686d3bea7bd	${rolesScopeConsentText}	consent.screen.text
214d076c-cb63-47fd-867b-0686d3bea7bd	false	include.in.token.scope
9cbc56ff-df36-4b4b-884d-e98732737867	false	display.on.consent.screen
9cbc56ff-df36-4b4b-884d-e98732737867		consent.screen.text
9cbc56ff-df36-4b4b-884d-e98732737867	false	include.in.token.scope
8fa29864-971f-4c81-9d21-12aaea3be7dd	false	display.on.consent.screen
8fa29864-971f-4c81-9d21-12aaea3be7dd	true	include.in.token.scope
fb3d66d0-362f-4feb-a772-3c8a81766f8c	false	display.on.consent.screen
fb3d66d0-362f-4feb-a772-3c8a81766f8c	false	include.in.token.scope
ba724387-db2e-430a-879b-6ec46f406df2	false	display.on.consent.screen
ba724387-db2e-430a-879b-6ec46f406df2	false	include.in.token.scope
\.


--
-- Data for Name: client_scope_client; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_scope_client (client_id, scope_id, default_scope) FROM stdin;
28a13f19-a581-48cf-9d27-203c80b5be3a	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
28a13f19-a581-48cf-9d27-203c80b5be3a	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
28a13f19-a581-48cf-9d27-203c80b5be3a	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
28a13f19-a581-48cf-9d27-203c80b5be3a	fa3301c7-ea7f-4983-a85e-999570232089	t
28a13f19-a581-48cf-9d27-203c80b5be3a	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
28a13f19-a581-48cf-9d27-203c80b5be3a	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
28a13f19-a581-48cf-9d27-203c80b5be3a	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
28a13f19-a581-48cf-9d27-203c80b5be3a	e7de7027-5f94-4eea-a86e-1b709749eb45	f
28a13f19-a581-48cf-9d27-203c80b5be3a	b996718d-07af-4a21-a55f-4725e56f65d6	f
28a13f19-a581-48cf-9d27-203c80b5be3a	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	fa3301c7-ea7f-4983-a85e-999570232089	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	e7de7027-5f94-4eea-a86e-1b709749eb45	f
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	b996718d-07af-4a21-a55f-4725e56f65d6	f
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
dbc511ea-0fcb-482e-ad99-f94b603da0a8	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	fa3301c7-ea7f-4983-a85e-999570232089	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
dbc511ea-0fcb-482e-ad99-f94b603da0a8	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
dbc511ea-0fcb-482e-ad99-f94b603da0a8	e7de7027-5f94-4eea-a86e-1b709749eb45	f
dbc511ea-0fcb-482e-ad99-f94b603da0a8	b996718d-07af-4a21-a55f-4725e56f65d6	f
dbc511ea-0fcb-482e-ad99-f94b603da0a8	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	fa3301c7-ea7f-4983-a85e-999570232089	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	e7de7027-5f94-4eea-a86e-1b709749eb45	f
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	b996718d-07af-4a21-a55f-4725e56f65d6	f
f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
25a276e3-07eb-49e9-86a9-5a15a5f09800	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	fa3301c7-ea7f-4983-a85e-999570232089	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
25a276e3-07eb-49e9-86a9-5a15a5f09800	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
25a276e3-07eb-49e9-86a9-5a15a5f09800	e7de7027-5f94-4eea-a86e-1b709749eb45	f
25a276e3-07eb-49e9-86a9-5a15a5f09800	b996718d-07af-4a21-a55f-4725e56f65d6	f
25a276e3-07eb-49e9-86a9-5a15a5f09800	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
c9127146-5188-4383-bc83-8371c445ed88	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
c9127146-5188-4383-bc83-8371c445ed88	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
c9127146-5188-4383-bc83-8371c445ed88	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
c9127146-5188-4383-bc83-8371c445ed88	fa3301c7-ea7f-4983-a85e-999570232089	t
c9127146-5188-4383-bc83-8371c445ed88	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
c9127146-5188-4383-bc83-8371c445ed88	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
c9127146-5188-4383-bc83-8371c445ed88	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
c9127146-5188-4383-bc83-8371c445ed88	e7de7027-5f94-4eea-a86e-1b709749eb45	f
c9127146-5188-4383-bc83-8371c445ed88	b996718d-07af-4a21-a55f-4725e56f65d6	f
c9127146-5188-4383-bc83-8371c445ed88	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
6d6f00fd-79c0-4acc-a3de-b28063ec0926	214d076c-cb63-47fd-867b-0686d3bea7bd	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	9cbc56ff-df36-4b4b-884d-e98732737867	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	b6128b6c-a696-4741-ae21-17d2141078a2	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	ba724387-db2e-430a-879b-6ec46f406df2	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
6d6f00fd-79c0-4acc-a3de-b28063ec0926	05563931-429a-4f06-8e68-5dca524f810f	f
6d6f00fd-79c0-4acc-a3de-b28063ec0926	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
6d6f00fd-79c0-4acc-a3de-b28063ec0926	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
6d6f00fd-79c0-4acc-a3de-b28063ec0926	bb96564a-5296-4a0b-973c-d7d57122fa10	f
d2e77719-c7fa-48e1-9d93-95b5f409862a	214d076c-cb63-47fd-867b-0686d3bea7bd	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	9cbc56ff-df36-4b4b-884d-e98732737867	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	b6128b6c-a696-4741-ae21-17d2141078a2	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	ba724387-db2e-430a-879b-6ec46f406df2	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
d2e77719-c7fa-48e1-9d93-95b5f409862a	05563931-429a-4f06-8e68-5dca524f810f	f
d2e77719-c7fa-48e1-9d93-95b5f409862a	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
d2e77719-c7fa-48e1-9d93-95b5f409862a	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
d2e77719-c7fa-48e1-9d93-95b5f409862a	bb96564a-5296-4a0b-973c-d7d57122fa10	f
809440f4-80ef-45a3-be47-4b824e521f2c	214d076c-cb63-47fd-867b-0686d3bea7bd	t
809440f4-80ef-45a3-be47-4b824e521f2c	9cbc56ff-df36-4b4b-884d-e98732737867	t
809440f4-80ef-45a3-be47-4b824e521f2c	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
809440f4-80ef-45a3-be47-4b824e521f2c	b6128b6c-a696-4741-ae21-17d2141078a2	t
809440f4-80ef-45a3-be47-4b824e521f2c	ba724387-db2e-430a-879b-6ec46f406df2	t
809440f4-80ef-45a3-be47-4b824e521f2c	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
809440f4-80ef-45a3-be47-4b824e521f2c	05563931-429a-4f06-8e68-5dca524f810f	f
809440f4-80ef-45a3-be47-4b824e521f2c	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
809440f4-80ef-45a3-be47-4b824e521f2c	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
809440f4-80ef-45a3-be47-4b824e521f2c	bb96564a-5296-4a0b-973c-d7d57122fa10	f
3c612010-d61f-4061-adb1-a09a4b7c2a51	214d076c-cb63-47fd-867b-0686d3bea7bd	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	9cbc56ff-df36-4b4b-884d-e98732737867	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	b6128b6c-a696-4741-ae21-17d2141078a2	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	ba724387-db2e-430a-879b-6ec46f406df2	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
3c612010-d61f-4061-adb1-a09a4b7c2a51	05563931-429a-4f06-8e68-5dca524f810f	f
3c612010-d61f-4061-adb1-a09a4b7c2a51	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
3c612010-d61f-4061-adb1-a09a4b7c2a51	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
3c612010-d61f-4061-adb1-a09a4b7c2a51	bb96564a-5296-4a0b-973c-d7d57122fa10	f
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	214d076c-cb63-47fd-867b-0686d3bea7bd	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	9cbc56ff-df36-4b4b-884d-e98732737867	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	b6128b6c-a696-4741-ae21-17d2141078a2	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	ba724387-db2e-430a-879b-6ec46f406df2	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	05563931-429a-4f06-8e68-5dca524f810f	f
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
8dec21bc-3dcc-4aff-8c3a-efa74fef5914	bb96564a-5296-4a0b-973c-d7d57122fa10	f
94b40267-f844-4f8e-996e-3bc5b0800c08	214d076c-cb63-47fd-867b-0686d3bea7bd	t
94b40267-f844-4f8e-996e-3bc5b0800c08	9cbc56ff-df36-4b4b-884d-e98732737867	t
94b40267-f844-4f8e-996e-3bc5b0800c08	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
94b40267-f844-4f8e-996e-3bc5b0800c08	b6128b6c-a696-4741-ae21-17d2141078a2	t
94b40267-f844-4f8e-996e-3bc5b0800c08	ba724387-db2e-430a-879b-6ec46f406df2	t
94b40267-f844-4f8e-996e-3bc5b0800c08	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
94b40267-f844-4f8e-996e-3bc5b0800c08	05563931-429a-4f06-8e68-5dca524f810f	f
94b40267-f844-4f8e-996e-3bc5b0800c08	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
94b40267-f844-4f8e-996e-3bc5b0800c08	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
94b40267-f844-4f8e-996e-3bc5b0800c08	bb96564a-5296-4a0b-973c-d7d57122fa10	f
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	214d076c-cb63-47fd-867b-0686d3bea7bd	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	9cbc56ff-df36-4b4b-884d-e98732737867	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	b6128b6c-a696-4741-ae21-17d2141078a2	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	ba724387-db2e-430a-879b-6ec46f406df2	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	05563931-429a-4f06-8e68-5dca524f810f	f
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	bb96564a-5296-4a0b-973c-d7d57122fa10	f
710ee357-9495-4b0b-8f44-907835d002b3	214d076c-cb63-47fd-867b-0686d3bea7bd	t
710ee357-9495-4b0b-8f44-907835d002b3	9cbc56ff-df36-4b4b-884d-e98732737867	t
710ee357-9495-4b0b-8f44-907835d002b3	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
710ee357-9495-4b0b-8f44-907835d002b3	b6128b6c-a696-4741-ae21-17d2141078a2	t
710ee357-9495-4b0b-8f44-907835d002b3	ba724387-db2e-430a-879b-6ec46f406df2	t
710ee357-9495-4b0b-8f44-907835d002b3	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
710ee357-9495-4b0b-8f44-907835d002b3	05563931-429a-4f06-8e68-5dca524f810f	f
710ee357-9495-4b0b-8f44-907835d002b3	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
710ee357-9495-4b0b-8f44-907835d002b3	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
710ee357-9495-4b0b-8f44-907835d002b3	bb96564a-5296-4a0b-973c-d7d57122fa10	f
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	214d076c-cb63-47fd-867b-0686d3bea7bd	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	9cbc56ff-df36-4b4b-884d-e98732737867	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	b6128b6c-a696-4741-ae21-17d2141078a2	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	ba724387-db2e-430a-879b-6ec46f406df2	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	05563931-429a-4f06-8e68-5dca524f810f	f
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	bb96564a-5296-4a0b-973c-d7d57122fa10	f
\.


--
-- Data for Name: client_scope_role_mapping; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_scope_role_mapping (scope_id, role_id) FROM stdin;
e7de7027-5f94-4eea-a86e-1b709749eb45	f751e3a5-e8da-4298-aa6b-38d8cc932fe5
05563931-429a-4f06-8e68-5dca524f810f	881460b5-a8c5-496f-a49d-827b4abccdc6
\.


--
-- Data for Name: client_session; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_session (id, client_id, redirect_uri, state, "timestamp", session_id, auth_method, realm_id, auth_user_id, current_action) FROM stdin;
\.


--
-- Data for Name: client_session_auth_status; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_session_auth_status (authenticator, status, client_session) FROM stdin;
\.


--
-- Data for Name: client_session_note; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_session_note (name, value, client_session) FROM stdin;
\.


--
-- Data for Name: client_session_prot_mapper; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_session_prot_mapper (protocol_mapper_id, client_session) FROM stdin;
\.


--
-- Data for Name: client_session_role; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_session_role (role_id, client_session) FROM stdin;
\.


--
-- Data for Name: client_user_session_note; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.client_user_session_note (name, value, client_session) FROM stdin;
\.


--
-- Data for Name: component; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.component (id, name, parent_id, provider_id, provider_type, realm_id, sub_type) FROM stdin;
c1b6e004-3798-49f7-8f5d-601e151d79f4	Trusted Hosts	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	trusted-hosts	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
ac6e8074-89a0-421d-adb7-2468ac8d1dcb	Consent Required	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	consent-required	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
939ba3d2-c943-408a-bd39-4ce38b0ab68b	Full Scope Disabled	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	scope	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
7092fa76-6ff3-425e-b09f-ef7bc15ea028	Max Clients Limit	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	max-clients	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
a4011535-aa4a-4e4b-8f62-da64821fd17e	Allowed Protocol Mapper Types	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
3924d99a-daab-4a3c-a44c-6426789e9442	Allowed Client Scopes	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	anonymous
faee9338-6440-4395-9eef-9da1f07ef295	Allowed Protocol Mapper Types	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	authenticated
71c4b89e-a969-429c-87e2-55aca90d7389	Allowed Client Scopes	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	authenticated
a0686b8b-86eb-4b5a-aeb4-08559109cec7	rsa-generated	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	rsa-generated	org.keycloak.keys.KeyProvider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N
ce4ca93f-6590-470a-a983-709b22b64597	rsa-enc-generated	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	rsa-enc-generated	org.keycloak.keys.KeyProvider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N
fcf0a754-1a66-494d-a5bf-0888a64d5334	hmac-generated-hs512	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	hmac-generated	org.keycloak.keys.KeyProvider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N
976db65d-4af9-4969-83af-30e13bef4285	aes-generated	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	aes-generated	org.keycloak.keys.KeyProvider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N
74edfd53-4fe6-4eff-b188-adf43bfaf2b6	\N	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	declarative-user-profile	org.keycloak.userprofile.UserProfileProvider	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N
5068578b-1f2f-4d5c-a5a8-9fbbfb54eb3a	rsa-generated	6a264182-ab2b-4da7-a868-c7dddf4329f2	rsa-generated	org.keycloak.keys.KeyProvider	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N
1559f8cd-72b5-40f7-bb33-42da34a34d88	rsa-enc-generated	6a264182-ab2b-4da7-a868-c7dddf4329f2	rsa-enc-generated	org.keycloak.keys.KeyProvider	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N
16eda227-cf16-4b75-b661-8b92fbd02e36	hmac-generated-hs512	6a264182-ab2b-4da7-a868-c7dddf4329f2	hmac-generated	org.keycloak.keys.KeyProvider	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N
a3f53330-d625-4bb3-94d4-fc022dc23573	aes-generated	6a264182-ab2b-4da7-a868-c7dddf4329f2	aes-generated	org.keycloak.keys.KeyProvider	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N
309877f3-3f5d-43dd-bb9f-f218804dd4d6	Trusted Hosts	6a264182-ab2b-4da7-a868-c7dddf4329f2	trusted-hosts	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
c70e2f35-a03c-43ac-9918-c36eddb924c4	Consent Required	6a264182-ab2b-4da7-a868-c7dddf4329f2	consent-required	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
3108f873-cc42-4038-84da-aeccb6354acd	Full Scope Disabled	6a264182-ab2b-4da7-a868-c7dddf4329f2	scope	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
c6b04a9c-5cd6-4ff3-bd25-16de37a8fa99	Max Clients Limit	6a264182-ab2b-4da7-a868-c7dddf4329f2	max-clients	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
d4f96d43-51a6-4991-b4e5-6502df6a72a3	Allowed Protocol Mapper Types	6a264182-ab2b-4da7-a868-c7dddf4329f2	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
2e1ddbba-e47d-4f96-8f7d-bbbb23888c42	Allowed Client Scopes	6a264182-ab2b-4da7-a868-c7dddf4329f2	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	anonymous
19620fcd-23c8-47bd-b9f6-8b4b106c8279	Allowed Protocol Mapper Types	6a264182-ab2b-4da7-a868-c7dddf4329f2	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	authenticated
3727515c-c052-493e-8aab-9c8a169573ef	Allowed Client Scopes	6a264182-ab2b-4da7-a868-c7dddf4329f2	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	authenticated
\.


--
-- Data for Name: component_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.component_config (id, component_id, name, value) FROM stdin;
4ea635b3-b43d-4c7e-9eb8-aca09caee458	7092fa76-6ff3-425e-b09f-ef7bc15ea028	max-clients	200
cf5e2ec9-20d6-4149-b828-64143f2f1fe0	3924d99a-daab-4a3c-a44c-6426789e9442	allow-default-scopes	true
7aff48b5-ee6d-4f9f-8dae-88c000dc5758	71c4b89e-a969-429c-87e2-55aca90d7389	allow-default-scopes	true
dd394239-6f65-4f01-a368-3e050f43b2c7	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	saml-role-list-mapper
b3ca48ce-cbb3-4bc7-a20f-6f3ba7f975a8	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	saml-user-attribute-mapper
a08b1658-188c-4f64-875d-86cd87524ea6	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
da4a4f51-271c-4912-9dc8-e8b2aa1770a6	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	saml-user-property-mapper
3bd02208-3743-4d10-9a9d-8231bb3595de	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
6fb84f82-2ba0-437d-8c6d-77cb5ae48020	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	oidc-full-name-mapper
defc92af-b187-4738-b396-9065a6e6aa42	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
496b8232-9e52-4f4c-a3b9-c6eab27d0f41	faee9338-6440-4395-9eef-9da1f07ef295	allowed-protocol-mapper-types	oidc-address-mapper
4c3af20c-9c30-46bf-b154-372721472e91	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
2be6e50a-0b40-4c5a-b2a2-b151a8a3feed	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	saml-role-list-mapper
d27a3ccf-315e-41be-8696-f88ef0fc5593	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	saml-user-attribute-mapper
4316a6fd-99e8-4693-964f-8497bc72ed03	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	oidc-full-name-mapper
3b56eddd-b6ec-4f19-8fc4-1f53dc34680a	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
1e5e9fe4-8db0-4fbd-8114-23d1d4fb89d0	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	saml-user-property-mapper
d4fbbbc4-de13-468a-ad17-a83704e927a7	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
56fef18a-aeb1-478c-bf71-a22defa23577	a4011535-aa4a-4e4b-8f62-da64821fd17e	allowed-protocol-mapper-types	oidc-address-mapper
9ffc677e-d489-400d-9b6e-b1e4ac5c138e	c1b6e004-3798-49f7-8f5d-601e151d79f4	client-uris-must-match	true
0da668b7-20db-49dc-a4e8-b8caf1b440a2	c1b6e004-3798-49f7-8f5d-601e151d79f4	host-sending-registration-request-must-match	true
2bb34e3e-38c4-4a7f-8ca6-3bf8caa79293	fcf0a754-1a66-494d-a5bf-0888a64d5334	algorithm	HS512
a9ca3d4e-8894-454e-b955-0432b51de011	fcf0a754-1a66-494d-a5bf-0888a64d5334	priority	100
a6d52904-26a0-4aa3-85bf-db90f9275c50	fcf0a754-1a66-494d-a5bf-0888a64d5334	secret	JGcBPFyXfeA5EwdB77DooYbKPxZy8NEQkwxTTNu3TstdkFQOu-XSsM6K6ovFAfp-AAWnLrshViU379TxusRhadS8-v10_c2EhwFIhFJCrogOcY23klopPNORBJL-h56QPUVV-CGf1hfG_R_T8aie2QIQiHRjauqIStze5Aq_Ei8
2248dd21-22ee-4a75-bfdd-8c49b908decc	fcf0a754-1a66-494d-a5bf-0888a64d5334	kid	8f8a2cb8-3bbf-407f-bf68-d38de8204d7d
09cd0e26-56ee-4a25-a273-dbe39ffa3667	a0686b8b-86eb-4b5a-aeb4-08559109cec7	priority	100
a95b33a0-b707-4949-91b8-1a861a405577	a0686b8b-86eb-4b5a-aeb4-08559109cec7	privateKey	MIIEowIBAAKCAQEA0vCVqU3CYBbm6UK6+2GXh5IrSK9j//PG6iUwRG3xMQZtl7/rsS1qBGt67kKSpFLWg9ERY986cPnvoBa77YtKiiHW6yx4++bJZAqnmfk/hP68QZjxiAIGvFA4jsHNXH92acpz4puqbnZ434uPmZDJ3z7doYjcxyWQ+8kYy/izHtDtClIX3+p1mgRnZ6dWg/0U+/lGtB17QIb7xfwjrkpXpHvF149edIUCTuBIe2u4YGZsFLBtB0KjAmUBlvmSxCazzHAthxHpLl0+nd6vnMVfw7SrRypX2Ik92c/dlmVASbklQvyzTN9kDayCucWC/mZwb4O9TRoEEudoP4j2CIggwQIDAQABAoIBAAbVJyvi6msSuCu8bx0Ua1mcrk0+QnwjHoGCxIj651yiANZxBNvqL4HGz3u8k/kW+9Qs51DNBXIXuR9+N7Ej7r1XB5n6M020NeLJMOZHu2XTRdrOxEgWX2HQgWcnt5S0RkF6qX1LczOnymuHSZanqM+pPs7sMCaSkhstx4wChB7Ohj7nB74VzKkCtBBmkudLIrKgOg+WGNwNkqs8QKowV/iGv89dCssLst75t99imJTcrDU9Swrt2mP5x/qQG0o68ikK6z/uHrxc0dXRAPRQJW+3kpH4URbjHKkm9Q3CbExPVyTiww1inWxt8z8KN6vORCG77x5lahJ17jC9OaV0zqECgYEA+fQFqgjap3F8WCJusjVuIzyYwT0jBhgIxEyjt5uRE0mb34FR980XZ+hy+ktDqcGsMv9mHC3eR0+qFfnCLHDnzpg7LBVx7jy2x3hGG/zvWM4YhCf8FYecu5DJEBgtBfZ+xKSVQjtBciTno1psQX6mg/7VRDLiINH/HUcVaAZL2AkCgYEA2ArzF4qe1wExucwWqHaXOeQqy2Qv2M+F8rf2iEdsDDv/CFnLirNtnPjL8xE1OdZ4pt/ESEKfWaYMELICLObxv648+EG5i9Gvr+PKnETWCYxuZKO03935U4X+EzXOVvpqDr+otdmFU6UcdmrE66I08nMgK5nxZ5RwLv4RtPVrAPkCgYBXRDQqDldQuJWCK9tcCr1+PezTIqY0vXVqG5vZQc4f3sY1/W+BxbATThu+eUKRZRXa5EJhOj5txUmLzJxXab/06D9Yf9A8LiRedgZ8RQ3HgoUatt8TITq+XallHhuyBkJyI0gdTJTn5iydYreDElXOpc0Nt3otnUOllCjMHc6jCQKBgQCiO+a8oO4SyuTKf0Xsj9GUOZEhV0TO7VfLIvZQ9EFhFpS3cqb0qzT/EZ4mE6ACpNnJhnPhR5ZePeEFkIctrOeRZ4iFbOWm53mk/cwieVa5qOklTgH/srMOU6quRlOC4V1PYgGRPZ1vaKftDNR/ljlob6eS1nF/tOphf41QdJM8EQKBgCzzn/q4wRFWJIAyHsQ2USi2BEI6h6yo7Hu2XftRiNFFOSiYG5hEmvu1EFRD7tdOVxnXHKh0XfKPVO9ngeKwzwCgAlh54RaPEzbvf9dYSN9KtRyh2/3ZU1J07bM2Ny2b0vHoqCQ7HC3jXH49WMphISfE0bZwSSwFOfHqod7ZBXTD
13633ddc-05a0-445d-9273-bb3ae3edfbc3	a0686b8b-86eb-4b5a-aeb4-08559109cec7	keyUse	SIG
4100626e-3179-442d-b505-b1234d2730cd	a0686b8b-86eb-4b5a-aeb4-08559109cec7	certificate	MIICmzCCAYMCBgGerZC56DANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjYwNjA5MTgwNTAzWhcNMzYwNjA5MTgwNjQzWjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDS8JWpTcJgFubpQrr7YZeHkitIr2P/88bqJTBEbfExBm2Xv+uxLWoEa3ruQpKkUtaD0RFj3zpw+e+gFrvti0qKIdbrLHj75slkCqeZ+T+E/rxBmPGIAga8UDiOwc1cf3ZpynPim6pudnjfi4+ZkMnfPt2hiNzHJZD7yRjL+LMe0O0KUhff6nWaBGdnp1aD/RT7+Ua0HXtAhvvF/COuSleke8XXj150hQJO4Eh7a7hgZmwUsG0HQqMCZQGW+ZLEJrPMcC2HEekuXT6d3q+cxV/DtKtHKlfYiT3Zz92WZUBJuSVC/LNM32QNrIK5xYL+ZnBvg71NGgQS52g/iPYIiCDBAgMBAAEwDQYJKoZIhvcNAQELBQADggEBABuoKCK3FhOCPER4jgtXcih97RN9UzQSCVoDexWa3arQezy8O4UgauCksqWN8mPuPPukR+Wd+ZbyX0D/51RD5VUa++FrKmRUmK8RLxkIxZ+2FB93JHdaNYv0YIn/jst66fXj0NX2J2Dz6V33BKHUAcjC2d8r7aj3Re1D1RLMiscQigyS3ZiqDAGgtDgJcxPEeRi3NeciE8QsPEJKNSySvVqC6hNn+nmOk6boH9qXYbPN36QEzQd6zM5FisLpLwBWjcEC/SUgvGE0OKcl6p6mr8rvWMslBIXojFb4YEJawa9cI1Wyepdj3TmO/hxiafIFJnMD52Iw3QBwkzYugiUiLJU=
1e01360b-1bd6-4e47-baa2-1aef14fd1282	976db65d-4af9-4969-83af-30e13bef4285	priority	100
e055d8a6-8bb5-45be-b20e-e9b19004f430	976db65d-4af9-4969-83af-30e13bef4285	secret	2pjvR4TVIMhGSn7agl46cQ
f00f64a9-c0c5-427c-be06-794719901293	976db65d-4af9-4969-83af-30e13bef4285	kid	2f1b6dd9-e33a-4fa0-8235-d0c7334b9944
b006bf1a-34dd-4e09-8f13-964758e873d5	5068578b-1f2f-4d5c-a5a8-9fbbfb54eb3a	priority	100
0ffd7132-74d2-4261-ae5c-b5deab29423c	1559f8cd-72b5-40f7-bb33-42da34a34d88	priority	100
1024c0ce-d114-4276-b005-ae357676ef70	1559f8cd-72b5-40f7-bb33-42da34a34d88	algorithm	RSA-OAEP
f45570b3-cb65-44b6-ba69-5798ad04ed64	1559f8cd-72b5-40f7-bb33-42da34a34d88	keyUse	ENC
3d515f46-8fc8-4ba4-b27e-127da43d8b3e	74edfd53-4fe6-4eff-b188-adf43bfaf2b6	kc.user.profile.config	{"attributes":[{"name":"username","displayName":"${username}","validations":{"length":{"min":3,"max":255},"username-prohibited-characters":{},"up-username-not-idn-homograph":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"email","displayName":"${email}","validations":{"email":{},"length":{"max":255}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"firstName","displayName":"${firstName}","validations":{"length":{"max":255},"person-name-prohibited-characters":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"lastName","displayName":"${lastName}","validations":{"length":{"max":255},"person-name-prohibited-characters":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false}],"groups":[{"name":"user-metadata","displayHeader":"User metadata","displayDescription":"Attributes, which refer to user metadata"}]}
8171aba3-a3f0-4e5d-be80-02d1df4e6eb0	ce4ca93f-6590-470a-a983-709b22b64597	priority	100
ad3a2b97-606c-4989-9ad7-91b19ab24195	ce4ca93f-6590-470a-a983-709b22b64597	keyUse	ENC
4b695c9b-27dd-4434-af9c-7ebd1605a7e5	ce4ca93f-6590-470a-a983-709b22b64597	privateKey	MIIEowIBAAKCAQEAw83pLHTlSd0GYBrZyIkrL+I99fG16DkAA0gmGf335UWreqTv4XZ3B6jE6eKIqoYm25FLLtMW99YzwN40a57pJtaaU4DnVd+c+cngz72PuEYq90RimdTGWk8jQVMiBZXHMo9fBUd27hlpi0Z1o/UjjocKlyZiqXodF3fKzg8L3IDAjfWn6J0Iu5jeR0O83OrHZeTvIQclXrWyFPmvTdAEwD8nNTpda3vywBWqtpmlSyLnvS5dhEJQJQhVnckgw3l0W6WCDEKJNeorLmDe6Ai8n2d3AR1BrnYHe+51GilPH264jVGzvP9NrGj2DmZWgdjMDjNY9wrXjg3QI2v3mfai/wIDAQABAoIBABqpxIcoQpI6BdnlGM5PrNDaxxiMWfq4daxSESuC7lSLQIb1RNvNQkzfCjQrLp8XS4f6E2SEnDZoNdNIBEK6I1ewQNhUJQGy70ZYhkOOYFl1503qmF6y9HEXIQmOj4MhL+dOUgspqHlTKTss/2yx6gNI7QPuLItANLadumva7VY7o8anXGeAmBGRn4ieukQ/98bqLEQrJpywhLbbklLmT2VAaskOVRrsIdJ8gILMgr+wO5Cn/LYgIrInCIIcZGTwvrQQdwXAzmcasDDoHSkt6m5QemoPNGFuCsjstaAL3PZl5aKzW8yTWNzqAw7AA3lqwfZT2VhqX14P0DE1ZFsJg5kCgYEA6tl4672IFER8LP3hJQ9BZ/MSiqC2oZZ/HlHcB1swHHUC33hIL01xb3SdG6RYuPpk7xr15+6jNO+hyfB5iaIFanqLR7nRmU8yOII6rRZ6hGkQ5cltDM4fXZR1SJ+MbTdHKzmLXOc2FdjIL2NEP7tFb7CFgQDT4JlFFW3owHZNSYMCgYEA1XA9gC5XrjC+2+MruHyKoXKrmEnAh2HF6s17dl2QyBeu6CnELGEcXNadlR/5acy4yn3DsFHe115QZBPABgKaSWd/0foEk9eUWaV06mIK9LB0lvo8S2LJ4MpQh5KFyk9qzLvnWgCBFwC5tGScwHU3cPNAVNAoMDDO7/B5Mo5xU9UCgYAzP0N4xcIVEiC6vKfNq3eNVGh+YbWYqzuQBTLrVAW6n/oBg8DUuaSAOsUxy/okW1d9KbfxZYytt4DpjRUoaHegFZ+hBjZrqvF9jUV6kcYocLjkO8EVI0GK7SNutooxJvfbwdHccwPFXqnIVXQGKDpttepcDS8u+qMtmu9IWEhjOwKBgA+5QQ6cW2E9vhG83o+svRm/tNx3MnPGxCnUEXBa3DuhYwU/bnBGhyxfsyQ1Qs6EgmiIc04d+eirzghRXCgVMQCPW19Ap+2sSAWCpuZNarkz9qLYtHBpSq4AuYYDSU/qIdgLT7PVrazgJM4hS1ryR69OfELDQvKp5dTPRl5vF/IxAoGBAMkNkJWgqqaKZpA+KUzbvX12QeYrSJ/ogMT3yUKA/7vTCH0nAsLbqfVBPpcktzoepuCirQ/PpmLi2RgUMUZnPpLWObZNNVZrlT/PUsXVLLzcWWnSiOc3JfDqYMC+IEV6r4geoaIf5w6lLg8cHPGX7RDCx0Uf5A2K2cF6RjwPw9NY
8a026a0e-8ac5-42e7-9a89-76b294fde44b	ce4ca93f-6590-470a-a983-709b22b64597	algorithm	RSA-OAEP
424ef6aa-5509-420b-8a17-6d1b80c95397	ce4ca93f-6590-470a-a983-709b22b64597	certificate	MIICmzCCAYMCBgGerZC6xzANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjYwNjA5MTgwNTAzWhcNMzYwNjA5MTgwNjQzWjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDDzeksdOVJ3QZgGtnIiSsv4j318bXoOQADSCYZ/fflRat6pO/hdncHqMTp4oiqhibbkUsu0xb31jPA3jRrnukm1ppTgOdV35z5yeDPvY+4Rir3RGKZ1MZaTyNBUyIFlccyj18FR3buGWmLRnWj9SOOhwqXJmKpeh0Xd8rODwvcgMCN9afonQi7mN5HQ7zc6sdl5O8hByVetbIU+a9N0ATAPyc1Ol1re/LAFaq2maVLIue9Ll2EQlAlCFWdySDDeXRbpYIMQok16isuYN7oCLyfZ3cBHUGudgd77nUaKU8fbriNUbO8/02saPYOZlaB2MwOM1j3CteODdAja/eZ9qL/AgMBAAEwDQYJKoZIhvcNAQELBQADggEBAI2zbtdYj4Fjupcu4bwSrM0A+JeNehdxALhTxEgFaeB+GEDnJfdGn/aBa0lJokZnBP4csQt1u5hLQWrWiBksv32cftI53KzkPCydMKB0N3OFjsX1/ttlPQkL3EVlrtDpjyxIIiJ4YqlwJZtUy9b2YNRMvyO+Izy2e70/Od17KMSkYnJDhfXdobcHjgedQqNf2keg389h/8eEHDpgNoQuykjQcj7/owFPE8fTTq01GS1ym81dzCq+ltnjNd94cPeFdRPHfnN8oY8cHDZ1fCDsDQwS4uJ/kqofVreW6lrFatpwXNR1hyaJPVcNw6xxJM/NJrOcTtKcYDjmOt4+ns++Gb0=
6b79ceb9-852e-465c-b76b-8bcf2ffd18ca	16eda227-cf16-4b75-b661-8b92fbd02e36	secret	BSlszYCrqN2yfdLfu4OcBbI2rMfEO1W5pJTKodTMz0jKm64NGkl_6gGJYXIa54ydfWHzPTirTe2GeTE_qzyVEvcsViIKziS44vuJA0vzaNPz0qCiP8jDH3SekLECx-ikE6pWkTl_DgJyWhqvmzoRHFpmsZonM7bsPqKyMh5k4EE
08103948-92de-4049-854e-3248588bc388	16eda227-cf16-4b75-b661-8b92fbd02e36	priority	100
aa19e186-1c27-40c3-8cb6-c019af128290	16eda227-cf16-4b75-b661-8b92fbd02e36	algorithm	HS512
15813fbc-f5cf-45dd-a654-f43f8f49e25e	16eda227-cf16-4b75-b661-8b92fbd02e36	kid	522637f7-4d6e-4e3c-a5a0-2d6c83491bb0
7370d046-fb0d-4fae-9c1b-7a90ffe6bb93	a3f53330-d625-4bb3-94d4-fc022dc23573	priority	100
0aeff268-eb54-401b-b75b-92747fea984b	a3f53330-d625-4bb3-94d4-fc022dc23573	secret	glNtTdrb6WFcOLgzO4jCOg
59bba5f2-6b49-422d-bf5d-abc42240b68d	a3f53330-d625-4bb3-94d4-fc022dc23573	kid	6eff981a-b03d-47ba-a454-2d4909ea872e
a34a99c5-c41e-401f-86e3-e24550bd33e1	5068578b-1f2f-4d5c-a5a8-9fbbfb54eb3a	certificate	MIICmTCCAYECBgGerZDG4DANBgkqhkiG9w0BAQsFADAQMQ4wDAYDVQQDDAVwdWxzZTAeFw0yNjA2MDkxODA1MDdaFw0zNjA2MDkxODA2NDdaMBAxDjAMBgNVBAMMBXB1bHNlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvwuJes8cPnPblm8gDo1GCgwZwt8ZtOm19P21g9KC9QKmFF1d8yXJR4jGN+21qhfYEzo0iJ0NkPy7PNYAXSWUnEBK5wDkYrdaMYbT1g60WzmA+FgEIlGJHuQ+qGLjt0ZLrAirKlTCYT8jfTWQ8Fm7cq87GYpQzs/S8CCOKrQutuUShcCMXz+K7wdauaBm5eYty3lRc0OKp6cE81ND0N5O/Sei1pxMaKi+yrr1MFKqj7AzSKecwM9M3KzK5JiWP5blevtiF4kskNr2OXxKBur4tdieZvdiBaVYj5e+Cw6lD+kytoIm9a4Y3HPTE0j8CkBcYm9mZ2nUFLtXM7/fAybqJwIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQBQFfibTlk5qAKEXdzz3419GPx8B2+IGQrKO+utJUiez6scD6RbAffD0Ygkq2vcJjwdGEy8lAd5zXbF+T0YrCulWtCSZGPjyK6kFCrdlx9DBZYypN9uW7vhnaQ3E+VtsvD09hKwrOmcTclYz5kSFLvtJ/aO3q/Up/wqDVaXxXHNuAQPA9pspH2GIUVKdfF8gtmoTF7y09+e4dkueG/23pUJQRHaCkZHxZPpuQwkxj7lYhVAW17+S1OCxE3qMC85Q116vERGGd4UIQAiG4KYB0EmWJIFnXGVyR6gFREneHGp/xxfthpBDP8zCMy5ugqdpzbWKbsuPKoKnnE+txHXAVm0
8583e84a-957e-4fc6-be81-0a256a4cee74	5068578b-1f2f-4d5c-a5a8-9fbbfb54eb3a	privateKey	MIIEpAIBAAKCAQEAvwuJes8cPnPblm8gDo1GCgwZwt8ZtOm19P21g9KC9QKmFF1d8yXJR4jGN+21qhfYEzo0iJ0NkPy7PNYAXSWUnEBK5wDkYrdaMYbT1g60WzmA+FgEIlGJHuQ+qGLjt0ZLrAirKlTCYT8jfTWQ8Fm7cq87GYpQzs/S8CCOKrQutuUShcCMXz+K7wdauaBm5eYty3lRc0OKp6cE81ND0N5O/Sei1pxMaKi+yrr1MFKqj7AzSKecwM9M3KzK5JiWP5blevtiF4kskNr2OXxKBur4tdieZvdiBaVYj5e+Cw6lD+kytoIm9a4Y3HPTE0j8CkBcYm9mZ2nUFLtXM7/fAybqJwIDAQABAoIBAANFTUs+9HrVPPMsX94f6Q0O+/nsG+KPBcB1/3+MQRW0v+clWhBpmzKQUuRuO2f4FIjvvCqCldLfoMz/1O3DUPID38RorYBLJ04lwsatZcUSDPUzfI6h2rkeqzvyxXdDytPdKiEFZnaHwDHKkvqqbp0eBuL/DTcdM71MsWJlx072QWxnmH0T/LIBrGIo2ZCBU8nJcEyig3FZ021CtDGhBFpD5GV0k4IC1uHvtVmkxOmcKoKcM+ieBzCivejSu64ApSXru/d6dOxsKsMgxVIGK7m1UmsICz8/v7gC5IQ1x3crhReHPN7iue1YgHb7SkxbJiCYY8Iy6IT5e8MzWr1ESWECgYEA7z7B97uvQpcau2P9Xpn5I0TP5Tx4tm2DYsan46BWzF7k1fdli4WjIwG3cdQ0RuWRtcYWTnpD8Vn6aqix6AONdXYhS1ivtBLSUYE5hnFQ/ZFKnxcJyMDQopf8d9EssbJkPm8ZI2+wPO4NDwG7dv6SOBtziSYUZ6A9SLpa9eaAwQ8CgYEAzGyjHHiPa/BA9D/odQy/zDYRciEo0JuBANfDOrHZp0nIz01sYWFYdNIBZO8Hci41R3x5AINAG3khI6RA6zbxcivlEP4utlow/H7eudHz705MQdsAs3DeEqgQ4vOKaOGhL9GaNMdWqFmKZxh0ITDE2Qqhbju0od9FwpFTIKRmlWkCgYEAiMKQMKQKGH+2GT6cPHK59w5D5R9/RZEulM1IdZdXZrYsC5/DXVFEIyO9EIWkaI6cj5MvdybvJc0wl73dDOrS9z1S5PZKYh6MOWksUA0ApiJizLRntGl8GiXVfUyGRwHZydLKRPZ4gSv3LQfpeKknPol6rwCkk2QHBEb67iwYl8MCgYBips60b63vDhuag7jfu85Xc4RJypzSxyijSnypt6hs5dulxxxVhk/U2H/ZwMycGpaVsAkI6U4ns/X9KEg3+uTcDzjVUYUjdTUMtQExNZP92ZBNe63D6uUQpdC4ZYVXBgPuer1rWQOF7OgwxolMdyeYAlxTQTbzozccJVuzdgMXeQKBgQDq6p+tXLCjQHylv5AJFV+7kNd7JE7TRU/GnEXx//I7DvkX+TIV9Csm/xY8D6TncQOywDu8FceF8QxZ5NJh6Whe/B8R6diDfZiC2FMLfjgZgtZIpN7MjxwSj6fVCmbtXPHd7OaKgHGu2xBlm1OH68NFPZOBqpthgucKGwi14YOUZA==
447a6b51-f477-43c6-a28c-75e6af0770ca	5068578b-1f2f-4d5c-a5a8-9fbbfb54eb3a	keyUse	SIG
065a5499-e6c7-4cb1-98eb-3f5cd4fe29aa	1559f8cd-72b5-40f7-bb33-42da34a34d88	certificate	MIICmTCCAYECBgGerZDISDANBgkqhkiG9w0BAQsFADAQMQ4wDAYDVQQDDAVwdWxzZTAeFw0yNjA2MDkxODA1MDdaFw0zNjA2MDkxODA2NDdaMBAxDjAMBgNVBAMMBXB1bHNlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtUyx1WzcC+tRMkbXVQv+1eXynIuRerfs0x9RbVOXVoq/+TY6lPlu0eglxK/Rmz9hYdPUhn7SICkITrYimTaJ2frlPY8ikV26VBQrDidb1KnzcfAFqs1NEw8eFuK0RQw6wtJ+vQkyAs/Hg26gujOu2FJ0T8ZGCQI7TZuTg/cddg6OW4sYdfoCAOCXxr3uMzRnY/pBy++FN1z7sEG3WqAvvOwmJDGRSZ3zJGkNPKUoDAd0qqkEJPbOOzAhlxicvXjWtySrogXj4dxmAmYayayzLbWbP5TUwynTwlUbs+rarwQPHe9HuqXfCvuRLVgvlT/24JRnHzNvfUzRsVmuigN38QIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQBnVgbRCv9acVTZrAjWI8lO0aR+gI/eDK2hvAv2pyevfK9wVOR29YOrwVgjCKqDjDdayfEemf0oNG5OkNipq9oBqu2NyRHJptgORPhwVlJYIk0v0GgBoKdLel4odicYA7ZEoLdVagPnZF+8axmbWgRXS6NpiVcfrKMeofH8Y9aXdRfaSVuqtRyByiqKdMZkdrGAg83wgDnihQ3q9rEp5nIDH7VPrCK0wo/VlZ3+99kwqQrRTHoeupbnbo4nKjl04g4yhDcd1UJHT9wptEgxOkaJcgrInDz4C+lU8jEX0jQSfX+dotyhfzWn/Aizqupzx46/uJQwhxyR2DTHluONJOIY
de888954-d225-434a-a890-7210cff0ddc4	1559f8cd-72b5-40f7-bb33-42da34a34d88	privateKey	MIIEowIBAAKCAQEAtUyx1WzcC+tRMkbXVQv+1eXynIuRerfs0x9RbVOXVoq/+TY6lPlu0eglxK/Rmz9hYdPUhn7SICkITrYimTaJ2frlPY8ikV26VBQrDidb1KnzcfAFqs1NEw8eFuK0RQw6wtJ+vQkyAs/Hg26gujOu2FJ0T8ZGCQI7TZuTg/cddg6OW4sYdfoCAOCXxr3uMzRnY/pBy++FN1z7sEG3WqAvvOwmJDGRSZ3zJGkNPKUoDAd0qqkEJPbOOzAhlxicvXjWtySrogXj4dxmAmYayayzLbWbP5TUwynTwlUbs+rarwQPHe9HuqXfCvuRLVgvlT/24JRnHzNvfUzRsVmuigN38QIDAQABAoIBAFfc2F5XiHjaTRpxjI/x5UmiTCaj2RhBJKvYhKzYEwLk8U6EgnWKQLPHru4YSxvS5o3zjA62TX06hYUn7bKU5M/YMNrZkGYkp1VyBL+yQWXaC1pPeV+iaVTwQaPTsIu59oxOWQ+h8jO8oLNInOpAe97obufubiiVhUoCOMZ+ry9z46FfM3nNh1lHAVuFCgcESgnv7dXkUwOxHoNfn0MZS39ghky8H02M76WthhM7uCxv/nmAup8HmRm9mmkAopEZDsOZI4uVZakFcjzuOdtN2AvfVpKT/+Tn7nsngwUSsnOd+chZyi6vLgEVfZG1Z5uZVaMtZqptPph2Hy8lWyNqNzUCgYEA2qCRhMgovrdjk75TGCGoPNFzTEAV9dACi2u7zjOa/rnXpei+7avMqYhbiA0s9ILBNV146oSMVeOeZP+tmm5h0L6LHeVFZS7f23DosSspXLhvJD+THg7L8V/bh9VSb8GRxsoVA7s5fXvw+bk78t123qSt5Ym8kNa4j2uGaiwp5PsCgYEA1Eqd+VN8mvesqZv9AvahyIa6MQ5iLFoPmRKOi9FLqj+F+ZnBvdrlUtd0geYZZNr2kqoGDI4PoW4j5i1enavj2ais+DLbxte3STSDAhDG3w59DZCy46ID21jwk7YvDv+YM9odYvxCxt+TLKuhERR4YL9amTe9tezFBqQoUOTdCwMCgYAptmkNRINBoAvHrJB+Ei3fLLcq3S9TbxSNNUjn1sDDyQF0DiwffJ/X2MRd+OWS4T+rxuHDHPcJjBw0ePPOezD+etxgH9ZVr9PWMnyzEOEbZ7UM3XRcT8Zpjzh7eh/4Yp5Fp1jLFXWqk3MuskDV3ZtIb3MeUGFB4TXlZ0aGC1cS8QKBgQDEIySNZOstKkOmeO5sPH4BDSkdhdKCc7sRjCmTWI31/7bCg6KSzJkvzsxf773qhrtlih0IoIAkf+Q/GA/g0R00zjjxH9wafNdklVWtJN742yQC0nvVAK1bjXLIpnwX+WIgFhcsizEPGSWbEf9ADo+ho2oLQYrPeLAYkLaG9sybDQKBgH7m+AL1+FD4oKu2jN3yhc8K65U8Rs3ZxDojW4eA9p1Y9pPLvN+5ojOW7UQRwPzbp58zYntx2GcQu/zADRn+6x/9xYLee04zLGF8mKQ54O/qZyO5VeI7Fv6Xh2eKQqZGm8g5hqgU7M6fbHG7hwB0wgNOwf+RwbkFaW9HW73lfLkz
0e6e167e-82e0-498d-8591-56842c2930ff	309877f3-3f5d-43dd-bb9f-f218804dd4d6	host-sending-registration-request-must-match	true
fcd5671e-e88d-45fc-943f-0243ca9b4e8e	309877f3-3f5d-43dd-bb9f-f218804dd4d6	client-uris-must-match	true
1fdfdc6d-b7bd-42ea-8ee0-7ad783dca9d8	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
cd735f25-ad15-41ec-96e1-d23e4bad8601	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	saml-user-attribute-mapper
7499469e-b787-44f0-b068-927e47ab518a	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	oidc-full-name-mapper
fba18ae1-adb7-4574-8e66-0d4e80460608	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	oidc-address-mapper
43a10736-b1f8-4c28-b15b-18d0c38e06e6	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	saml-user-property-mapper
ab0fdbc2-7367-4026-b4c3-663485da8986	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	saml-role-list-mapper
0d4670cf-aa18-4e71-81c3-63aba813d320	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
273c4a57-06b8-4938-9221-3ac59e33d7f0	d4f96d43-51a6-4991-b4e5-6502df6a72a3	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
7c5f7736-a682-42aa-8e87-e333eee01aea	2e1ddbba-e47d-4f96-8f7d-bbbb23888c42	allow-default-scopes	true
73af51dd-4b4a-4632-ad45-bc61e5332f70	c6b04a9c-5cd6-4ff3-bd25-16de37a8fa99	max-clients	200
7556d65e-ad47-4059-a377-5b5eadbefd65	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
f2065aa1-b6f5-4f4e-ba64-cbfce77807c6	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
68fdfb5c-dc47-4888-85e6-7af5418d9705	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	oidc-address-mapper
dd2b1f59-352d-498d-b598-d391fe4c316d	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	saml-user-property-mapper
43043ae7-00ad-4541-af3a-2288cd31b46a	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	saml-role-list-mapper
90157b8f-1363-4551-93de-9ed4d7e7d5f2	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	saml-user-attribute-mapper
e5abfc27-fdf0-41ea-95b2-f726a6be9bf8	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	oidc-full-name-mapper
30798a4d-8251-422c-a935-c37453e64564	19620fcd-23c8-47bd-b9f6-8b4b106c8279	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
4d767019-25ff-47c6-8525-26bdfd64598e	3727515c-c052-493e-8aab-9c8a169573ef	allow-default-scopes	true
\.


--
-- Data for Name: composite_role; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.composite_role (composite, child_role) FROM stdin;
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	34dce5e6-6ea9-46fe-949d-b86e27d16341
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	caa0ec3a-5274-4a30-b462-4d3db7775a3f
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	db4d346a-a1e7-484d-adae-4654608933a2
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	8cddcfc9-3959-4561-b59a-c5d401cbbb8e
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	e5b0777e-dee7-44d6-b419-cd7d56d73996
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	e58a23ef-dfca-48eb-84f8-916f17c8698e
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	d628ca16-19e4-47d5-b5e0-7bce7e2b0533
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	839416e9-e124-4009-857e-1e31bcf0b656
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	2937775c-79df-4924-b2bd-b4316b0a0d61
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	547a68c0-9a7a-4f48-81eb-a4d62cee05b1
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	42a3f5d8-bd3e-41a8-872f-c7fcc0ca31f6
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	15522bbd-c298-42c3-b2a5-f6da7ce842ee
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	b5cf9f07-6c41-464b-b26b-da8899f73dc5
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	7c325b53-f20c-474a-a75d-f2176cb6207c
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	5a3c68ed-bd91-4e44-afae-2999760b7006
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	5c509666-cb36-4d3e-a11f-bde89c621284
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	7f273eb2-8d47-43b2-b69f-f2ea5b202eff
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	e4ee5423-abc5-45bd-a2c0-151c32ae38da
8cddcfc9-3959-4561-b59a-c5d401cbbb8e	e4ee5423-abc5-45bd-a2c0-151c32ae38da
8cddcfc9-3959-4561-b59a-c5d401cbbb8e	5a3c68ed-bd91-4e44-afae-2999760b7006
c5f92874-1f2c-42cf-ad4f-a4ccf962cce9	063594c3-5561-4859-a81f-610e32b50a4a
e5b0777e-dee7-44d6-b419-cd7d56d73996	5c509666-cb36-4d3e-a11f-bde89c621284
c5f92874-1f2c-42cf-ad4f-a4ccf962cce9	ff571d5a-d56e-4937-a412-60049b740c33
ff571d5a-d56e-4937-a412-60049b740c33	1a983def-3178-4b56-882b-2204f99d96d8
86d0901e-138f-478e-96ce-d6336bbda074	42c2533c-2344-4f58-a033-d7bfa6a0b05d
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	b42c747d-9b0e-4bc3-b301-d89c739e68b9
c5f92874-1f2c-42cf-ad4f-a4ccf962cce9	f751e3a5-e8da-4298-aa6b-38d8cc932fe5
c5f92874-1f2c-42cf-ad4f-a4ccf962cce9	6fb9fb79-6498-4795-a21a-f5d24981ed62
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	1c065dd1-d8bc-46ef-90f3-6fedc4fdf66f
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	61a7e7c7-1c19-4526-9260-d05be634dd75
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	34d1863f-a724-4c37-90ea-ad092406e8d6
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	157a1a8c-2149-4992-aa7e-7c361a6739fe
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	e94828cf-57a3-4b7a-81eb-6025470c7845
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	44d1147b-6188-4de4-ae4a-c56079aeb97b
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	e1ea24c2-f5e4-44da-a7ef-a5be328c756b
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	409da1da-bc78-41e9-aba9-829be59fd9b0
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	128059cd-7f66-4548-bc02-0112423760fc
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	7dfed9d9-ff07-4bb5-9198-3fc70d8be076
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	2abe3551-dcde-44d2-bb41-2c6b43f2546f
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	f2edb580-16f3-40b6-a092-c1aeb72198b7
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	7fe7cbd9-ab4f-4412-808d-f96a601bde33
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	3fa0b7ab-ebe7-457a-97d7-3636cd9b499f
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	f6d7a6a9-6d79-4720-9534-f4d90ef8a068
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	8bad5d61-5fea-4525-9285-71bd5809461f
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	9fb820f1-8447-4d42-bfdb-1c984a6e54c5
157a1a8c-2149-4992-aa7e-7c361a6739fe	f6d7a6a9-6d79-4720-9534-f4d90ef8a068
34d1863f-a724-4c37-90ea-ad092406e8d6	3fa0b7ab-ebe7-457a-97d7-3636cd9b499f
34d1863f-a724-4c37-90ea-ad092406e8d6	9fb820f1-8447-4d42-bfdb-1c984a6e54c5
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	6d6f1ff4-f643-46c0-a6f1-e48e11671362
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	3d4db894-de9f-493d-a50f-bba47b85039e
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	7e098030-d97b-4651-82f4-3a3c3e60d097
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	6ea0f2d5-da8b-4789-88ed-c87b99c2d896
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	b5c2b21d-cba4-455d-8fd3-2d005ac9dfbf
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	f21ebbfa-9d0e-4cb3-a85f-c3a116ec5d75
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	de98959e-7cb0-4d63-8e73-b49672048e63
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	0f86459f-3f47-45ab-b493-909b1852fb03
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	a0ad5d4c-03eb-4226-8366-d076aaff720c
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	998df5d5-3e15-4f15-adca-c971c96a5aaf
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	8de0c1b1-27a3-4aef-b625-2d4778e70238
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	4d5886b4-432e-488b-aed1-89631c8993ef
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	1f47328a-3a1f-4219-aad5-924aaa302317
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	4b76e09c-26d0-40e4-8c69-9c9a10339f3e
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	de7df76b-ca64-4d61-887b-28df10251711
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	c317a900-d921-4688-b259-eb5fcb3e20a0
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	a34344e7-5369-49c1-971a-91a858989f43
6ea0f2d5-da8b-4789-88ed-c87b99c2d896	de7df76b-ca64-4d61-887b-28df10251711
7e098030-d97b-4651-82f4-3a3c3e60d097	4b76e09c-26d0-40e4-8c69-9c9a10339f3e
7e098030-d97b-4651-82f4-3a3c3e60d097	a34344e7-5369-49c1-971a-91a858989f43
c2043b06-2175-4019-89aa-9bef1b881b62	22da8887-f53f-4429-ab44-e535258762ed
c2043b06-2175-4019-89aa-9bef1b881b62	f53862a5-f9b3-462e-ba32-cfccb6990d3a
f53862a5-f9b3-462e-ba32-cfccb6990d3a	5275d222-efc0-4f67-af4d-a4ac35765e92
c2a6016a-7963-4854-9023-45d491ab5ba1	2c1cf615-6530-4c98-b689-66530eda52a5
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	eec11496-53b0-45e4-9704-17703d316efb
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	6545e5cd-6529-407d-8801-56e8ed73120a
c2043b06-2175-4019-89aa-9bef1b881b62	881460b5-a8c5-496f-a49d-827b4abccdc6
c2043b06-2175-4019-89aa-9bef1b881b62	3ed27b29-842c-45e8-85d1-86dc1e8352ea
c2043b06-2175-4019-89aa-9bef1b881b62	a302631e-097f-4ef2-b3d0-7f682a1b6979
\.


--
-- Data for Name: credential; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.credential (id, salt, type, user_id, created_date, user_label, secret_data, credential_data, priority) FROM stdin;
\.


--
-- Data for Name: databasechangelog; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.databasechangelog (id, author, filename, dateexecuted, orderexecuted, exectype, md5sum, description, comments, tag, liquibase, contexts, labels, deployment_id) FROM stdin;
1.0.0.Final-KEYCLOAK-5461	sthorger@redhat.com	META-INF/jpa-changelog-1.0.0.Final.xml	2026-06-09 19:06:36.870487	1	EXECUTED	9:6f1016664e21e16d26517a4418f5e3df	createTable tableName=APPLICATION_DEFAULT_ROLES; createTable tableName=CLIENT; createTable tableName=CLIENT_SESSION; createTable tableName=CLIENT_SESSION_ROLE; createTable tableName=COMPOSITE_ROLE; createTable tableName=CREDENTIAL; createTable tab...		\N	4.25.1	\N	\N	1028395744
1.0.0.Final-KEYCLOAK-5461	sthorger@redhat.com	META-INF/db2-jpa-changelog-1.0.0.Final.xml	2026-06-09 19:06:36.927107	2	MARK_RAN	9:828775b1596a07d1200ba1d49e5e3941	createTable tableName=APPLICATION_DEFAULT_ROLES; createTable tableName=CLIENT; createTable tableName=CLIENT_SESSION; createTable tableName=CLIENT_SESSION_ROLE; createTable tableName=COMPOSITE_ROLE; createTable tableName=CREDENTIAL; createTable tab...		\N	4.25.1	\N	\N	1028395744
1.1.0.Beta1	sthorger@redhat.com	META-INF/jpa-changelog-1.1.0.Beta1.xml	2026-06-09 19:06:37.058948	3	EXECUTED	9:5f090e44a7d595883c1fb61f4b41fd38	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=CLIENT_ATTRIBUTES; createTable tableName=CLIENT_SESSION_NOTE; createTable tableName=APP_NODE_REGISTRATIONS; addColumn table...		\N	4.25.1	\N	\N	1028395744
1.1.0.Final	sthorger@redhat.com	META-INF/jpa-changelog-1.1.0.Final.xml	2026-06-09 19:06:37.067601	4	EXECUTED	9:c07e577387a3d2c04d1adc9aaad8730e	renameColumn newColumnName=EVENT_TIME, oldColumnName=TIME, tableName=EVENT_ENTITY		\N	4.25.1	\N	\N	1028395744
1.2.0.Beta1	psilva@redhat.com	META-INF/jpa-changelog-1.2.0.Beta1.xml	2026-06-09 19:06:37.316477	5	EXECUTED	9:b68ce996c655922dbcd2fe6b6ae72686	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=PROTOCOL_MAPPER; createTable tableName=PROTOCOL_MAPPER_CONFIG; createTable tableName=...		\N	4.25.1	\N	\N	1028395744
1.2.0.Beta1	psilva@redhat.com	META-INF/db2-jpa-changelog-1.2.0.Beta1.xml	2026-06-09 19:06:37.32385	6	MARK_RAN	9:543b5c9989f024fe35c6f6c5a97de88e	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=PROTOCOL_MAPPER; createTable tableName=PROTOCOL_MAPPER_CONFIG; createTable tableName=...		\N	4.25.1	\N	\N	1028395744
1.2.0.RC1	bburke@redhat.com	META-INF/jpa-changelog-1.2.0.CR1.xml	2026-06-09 19:06:37.521794	7	EXECUTED	9:765afebbe21cf5bbca048e632df38336	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=MIGRATION_MODEL; createTable tableName=IDENTITY_P...		\N	4.25.1	\N	\N	1028395744
1.2.0.RC1	bburke@redhat.com	META-INF/db2-jpa-changelog-1.2.0.CR1.xml	2026-06-09 19:06:37.533264	8	MARK_RAN	9:db4a145ba11a6fdaefb397f6dbf829a1	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=MIGRATION_MODEL; createTable tableName=IDENTITY_P...		\N	4.25.1	\N	\N	1028395744
1.2.0.Final	keycloak	META-INF/jpa-changelog-1.2.0.Final.xml	2026-06-09 19:06:37.543585	9	EXECUTED	9:9d05c7be10cdb873f8bcb41bc3a8ab23	update tableName=CLIENT; update tableName=CLIENT; update tableName=CLIENT		\N	4.25.1	\N	\N	1028395744
1.3.0	bburke@redhat.com	META-INF/jpa-changelog-1.3.0.xml	2026-06-09 19:06:37.700697	10	EXECUTED	9:18593702353128d53111f9b1ff0b82b8	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=ADMI...		\N	4.25.1	\N	\N	1028395744
1.4.0	bburke@redhat.com	META-INF/jpa-changelog-1.4.0.xml	2026-06-09 19:06:37.792741	11	EXECUTED	9:6122efe5f090e41a85c0f1c9e52cbb62	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.25.1	\N	\N	1028395744
1.4.0	bburke@redhat.com	META-INF/db2-jpa-changelog-1.4.0.xml	2026-06-09 19:06:37.808997	12	MARK_RAN	9:e1ff28bf7568451453f844c5d54bb0b5	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.25.1	\N	\N	1028395744
1.5.0	bburke@redhat.com	META-INF/jpa-changelog-1.5.0.xml	2026-06-09 19:06:37.904822	13	EXECUTED	9:7af32cd8957fbc069f796b61217483fd	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.25.1	\N	\N	1028395744
1.6.1_from15	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-06-09 19:06:37.980903	14	EXECUTED	9:6005e15e84714cd83226bf7879f54190	addColumn tableName=REALM; addColumn tableName=KEYCLOAK_ROLE; addColumn tableName=CLIENT; createTable tableName=OFFLINE_USER_SESSION; createTable tableName=OFFLINE_CLIENT_SESSION; addPrimaryKey constraintName=CONSTRAINT_OFFL_US_SES_PK2, tableName=...		\N	4.25.1	\N	\N	1028395744
1.6.1_from16-pre	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-06-09 19:06:37.98723	15	MARK_RAN	9:bf656f5a2b055d07f314431cae76f06c	delete tableName=OFFLINE_CLIENT_SESSION; delete tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
1.6.1_from16	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-06-09 19:06:37.998002	16	MARK_RAN	9:f8dadc9284440469dcf71e25ca6ab99b	dropPrimaryKey constraintName=CONSTRAINT_OFFLINE_US_SES_PK, tableName=OFFLINE_USER_SESSION; dropPrimaryKey constraintName=CONSTRAINT_OFFLINE_CL_SES_PK, tableName=OFFLINE_CLIENT_SESSION; addColumn tableName=OFFLINE_USER_SESSION; update tableName=OF...		\N	4.25.1	\N	\N	1028395744
1.6.1	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-06-09 19:06:38.007786	17	EXECUTED	9:d41d8cd98f00b204e9800998ecf8427e	empty		\N	4.25.1	\N	\N	1028395744
1.7.0	bburke@redhat.com	META-INF/jpa-changelog-1.7.0.xml	2026-06-09 19:06:38.08826	18	EXECUTED	9:3368ff0be4c2855ee2dd9ca813b38d8e	createTable tableName=KEYCLOAK_GROUP; createTable tableName=GROUP_ROLE_MAPPING; createTable tableName=GROUP_ATTRIBUTE; createTable tableName=USER_GROUP_MEMBERSHIP; createTable tableName=REALM_DEFAULT_GROUPS; addColumn tableName=IDENTITY_PROVIDER; ...		\N	4.25.1	\N	\N	1028395744
1.8.0	mposolda@redhat.com	META-INF/jpa-changelog-1.8.0.xml	2026-06-09 19:06:38.168105	19	EXECUTED	9:8ac2fb5dd030b24c0570a763ed75ed20	addColumn tableName=IDENTITY_PROVIDER; createTable tableName=CLIENT_TEMPLATE; createTable tableName=CLIENT_TEMPLATE_ATTRIBUTES; createTable tableName=TEMPLATE_SCOPE_MAPPING; dropNotNullConstraint columnName=CLIENT_ID, tableName=PROTOCOL_MAPPER; ad...		\N	4.25.1	\N	\N	1028395744
1.8.0-2	keycloak	META-INF/jpa-changelog-1.8.0.xml	2026-06-09 19:06:38.176621	20	EXECUTED	9:f91ddca9b19743db60e3057679810e6c	dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; update tableName=CREDENTIAL		\N	4.25.1	\N	\N	1028395744
1.8.0	mposolda@redhat.com	META-INF/db2-jpa-changelog-1.8.0.xml	2026-06-09 19:06:38.181132	21	MARK_RAN	9:831e82914316dc8a57dc09d755f23c51	addColumn tableName=IDENTITY_PROVIDER; createTable tableName=CLIENT_TEMPLATE; createTable tableName=CLIENT_TEMPLATE_ATTRIBUTES; createTable tableName=TEMPLATE_SCOPE_MAPPING; dropNotNullConstraint columnName=CLIENT_ID, tableName=PROTOCOL_MAPPER; ad...		\N	4.25.1	\N	\N	1028395744
1.8.0-2	keycloak	META-INF/db2-jpa-changelog-1.8.0.xml	2026-06-09 19:06:38.186379	22	MARK_RAN	9:f91ddca9b19743db60e3057679810e6c	dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; update tableName=CREDENTIAL		\N	4.25.1	\N	\N	1028395744
1.9.0	mposolda@redhat.com	META-INF/jpa-changelog-1.9.0.xml	2026-06-09 19:06:38.24039	23	EXECUTED	9:bc3d0f9e823a69dc21e23e94c7a94bb1	update tableName=REALM; update tableName=REALM; update tableName=REALM; update tableName=REALM; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=REALM; update tableName=REALM; customChange; dr...		\N	4.25.1	\N	\N	1028395744
1.9.1	keycloak	META-INF/jpa-changelog-1.9.1.xml	2026-06-09 19:06:38.249813	24	EXECUTED	9:c9999da42f543575ab790e76439a2679	modifyDataType columnName=PRIVATE_KEY, tableName=REALM; modifyDataType columnName=PUBLIC_KEY, tableName=REALM; modifyDataType columnName=CERTIFICATE, tableName=REALM		\N	4.25.1	\N	\N	1028395744
1.9.1	keycloak	META-INF/db2-jpa-changelog-1.9.1.xml	2026-06-09 19:06:38.253437	25	MARK_RAN	9:0d6c65c6f58732d81569e77b10ba301d	modifyDataType columnName=PRIVATE_KEY, tableName=REALM; modifyDataType columnName=CERTIFICATE, tableName=REALM		\N	4.25.1	\N	\N	1028395744
1.9.2	keycloak	META-INF/jpa-changelog-1.9.2.xml	2026-06-09 19:06:38.323352	26	EXECUTED	9:fc576660fc016ae53d2d4778d84d86d0	createIndex indexName=IDX_USER_EMAIL, tableName=USER_ENTITY; createIndex indexName=IDX_USER_ROLE_MAPPING, tableName=USER_ROLE_MAPPING; createIndex indexName=IDX_USER_GROUP_MAPPING, tableName=USER_GROUP_MEMBERSHIP; createIndex indexName=IDX_USER_CO...		\N	4.25.1	\N	\N	1028395744
authz-2.0.0	psilva@redhat.com	META-INF/jpa-changelog-authz-2.0.0.xml	2026-06-09 19:06:38.448883	27	EXECUTED	9:43ed6b0da89ff77206289e87eaa9c024	createTable tableName=RESOURCE_SERVER; addPrimaryKey constraintName=CONSTRAINT_FARS, tableName=RESOURCE_SERVER; addUniqueConstraint constraintName=UK_AU8TT6T700S9V50BU18WS5HA6, tableName=RESOURCE_SERVER; createTable tableName=RESOURCE_SERVER_RESOU...		\N	4.25.1	\N	\N	1028395744
authz-2.5.1	psilva@redhat.com	META-INF/jpa-changelog-authz-2.5.1.xml	2026-06-09 19:06:38.4547	28	EXECUTED	9:44bae577f551b3738740281eceb4ea70	update tableName=RESOURCE_SERVER_POLICY		\N	4.25.1	\N	\N	1028395744
2.1.0-KEYCLOAK-5461	bburke@redhat.com	META-INF/jpa-changelog-2.1.0.xml	2026-06-09 19:06:38.560934	29	EXECUTED	9:bd88e1f833df0420b01e114533aee5e8	createTable tableName=BROKER_LINK; createTable tableName=FED_USER_ATTRIBUTE; createTable tableName=FED_USER_CONSENT; createTable tableName=FED_USER_CONSENT_ROLE; createTable tableName=FED_USER_CONSENT_PROT_MAPPER; createTable tableName=FED_USER_CR...		\N	4.25.1	\N	\N	1028395744
2.2.0	bburke@redhat.com	META-INF/jpa-changelog-2.2.0.xml	2026-06-09 19:06:38.59021	30	EXECUTED	9:a7022af5267f019d020edfe316ef4371	addColumn tableName=ADMIN_EVENT_ENTITY; createTable tableName=CREDENTIAL_ATTRIBUTE; createTable tableName=FED_CREDENTIAL_ATTRIBUTE; modifyDataType columnName=VALUE, tableName=CREDENTIAL; addForeignKeyConstraint baseTableName=FED_CREDENTIAL_ATTRIBU...		\N	4.25.1	\N	\N	1028395744
2.3.0	bburke@redhat.com	META-INF/jpa-changelog-2.3.0.xml	2026-06-09 19:06:38.630389	31	EXECUTED	9:fc155c394040654d6a79227e56f5e25a	createTable tableName=FEDERATED_USER; addPrimaryKey constraintName=CONSTR_FEDERATED_USER, tableName=FEDERATED_USER; dropDefaultValue columnName=TOTP, tableName=USER_ENTITY; dropColumn columnName=TOTP, tableName=USER_ENTITY; addColumn tableName=IDE...		\N	4.25.1	\N	\N	1028395744
2.4.0	bburke@redhat.com	META-INF/jpa-changelog-2.4.0.xml	2026-06-09 19:06:38.640617	32	EXECUTED	9:eac4ffb2a14795e5dc7b426063e54d88	customChange		\N	4.25.1	\N	\N	1028395744
2.5.0	bburke@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-06-09 19:06:38.652605	33	EXECUTED	9:54937c05672568c4c64fc9524c1e9462	customChange; modifyDataType columnName=USER_ID, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
2.5.0-unicode-oracle	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-06-09 19:06:38.655803	34	MARK_RAN	9:3a32bace77c84d7678d035a7f5a8084e	modifyDataType columnName=DESCRIPTION, tableName=AUTHENTICATION_FLOW; modifyDataType columnName=DESCRIPTION, tableName=CLIENT_TEMPLATE; modifyDataType columnName=DESCRIPTION, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=DESCRIPTION,...		\N	4.25.1	\N	\N	1028395744
2.5.0-unicode-other-dbs	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-06-09 19:06:38.704813	35	EXECUTED	9:33d72168746f81f98ae3a1e8e0ca3554	modifyDataType columnName=DESCRIPTION, tableName=AUTHENTICATION_FLOW; modifyDataType columnName=DESCRIPTION, tableName=CLIENT_TEMPLATE; modifyDataType columnName=DESCRIPTION, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=DESCRIPTION,...		\N	4.25.1	\N	\N	1028395744
2.5.0-duplicate-email-support	slawomir@dabek.name	META-INF/jpa-changelog-2.5.0.xml	2026-06-09 19:06:38.712297	36	EXECUTED	9:61b6d3d7a4c0e0024b0c839da283da0c	addColumn tableName=REALM		\N	4.25.1	\N	\N	1028395744
2.5.0-unique-group-names	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-06-09 19:06:38.721263	37	EXECUTED	9:8dcac7bdf7378e7d823cdfddebf72fda	addUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.25.1	\N	\N	1028395744
2.5.1	bburke@redhat.com	META-INF/jpa-changelog-2.5.1.xml	2026-06-09 19:06:38.72707	38	EXECUTED	9:a2b870802540cb3faa72098db5388af3	addColumn tableName=FED_USER_CONSENT		\N	4.25.1	\N	\N	1028395744
3.0.0	bburke@redhat.com	META-INF/jpa-changelog-3.0.0.xml	2026-06-09 19:06:38.733489	39	EXECUTED	9:132a67499ba24bcc54fb5cbdcfe7e4c0	addColumn tableName=IDENTITY_PROVIDER		\N	4.25.1	\N	\N	1028395744
3.2.0-fix	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-06-09 19:06:38.735563	40	MARK_RAN	9:938f894c032f5430f2b0fafb1a243462	addNotNullConstraint columnName=REALM_ID, tableName=CLIENT_INITIAL_ACCESS		\N	4.25.1	\N	\N	1028395744
3.2.0-fix-with-keycloak-5416	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-06-09 19:06:38.739559	41	MARK_RAN	9:845c332ff1874dc5d35974b0babf3006	dropIndex indexName=IDX_CLIENT_INIT_ACC_REALM, tableName=CLIENT_INITIAL_ACCESS; addNotNullConstraint columnName=REALM_ID, tableName=CLIENT_INITIAL_ACCESS; createIndex indexName=IDX_CLIENT_INIT_ACC_REALM, tableName=CLIENT_INITIAL_ACCESS		\N	4.25.1	\N	\N	1028395744
3.2.0-fix-offline-sessions	hmlnarik	META-INF/jpa-changelog-3.2.0.xml	2026-06-09 19:06:38.750171	42	EXECUTED	9:fc86359c079781adc577c5a217e4d04c	customChange		\N	4.25.1	\N	\N	1028395744
3.2.0-fixed	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-06-09 19:06:38.968204	43	EXECUTED	9:59a64800e3c0d09b825f8a3b444fa8f4	addColumn tableName=REALM; dropPrimaryKey constraintName=CONSTRAINT_OFFL_CL_SES_PK2, tableName=OFFLINE_CLIENT_SESSION; dropColumn columnName=CLIENT_SESSION_ID, tableName=OFFLINE_CLIENT_SESSION; addPrimaryKey constraintName=CONSTRAINT_OFFL_CL_SES_P...		\N	4.25.1	\N	\N	1028395744
3.3.0	keycloak	META-INF/jpa-changelog-3.3.0.xml	2026-06-09 19:06:38.974005	44	EXECUTED	9:d48d6da5c6ccf667807f633fe489ce88	addColumn tableName=USER_ENTITY		\N	4.25.1	\N	\N	1028395744
authz-3.4.0.CR1-resource-server-pk-change-part1	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-06-09 19:06:38.980332	45	EXECUTED	9:dde36f7973e80d71fceee683bc5d2951	addColumn tableName=RESOURCE_SERVER_POLICY; addColumn tableName=RESOURCE_SERVER_RESOURCE; addColumn tableName=RESOURCE_SERVER_SCOPE		\N	4.25.1	\N	\N	1028395744
authz-3.4.0.CR1-resource-server-pk-change-part2-KEYCLOAK-6095	hmlnarik@redhat.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-06-09 19:06:38.988143	46	EXECUTED	9:b855e9b0a406b34fa323235a0cf4f640	customChange		\N	4.25.1	\N	\N	1028395744
authz-3.4.0.CR1-resource-server-pk-change-part3-fixed	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-06-09 19:06:38.990361	47	MARK_RAN	9:51abbacd7b416c50c4421a8cabf7927e	dropIndex indexName=IDX_RES_SERV_POL_RES_SERV, tableName=RESOURCE_SERVER_POLICY; dropIndex indexName=IDX_RES_SRV_RES_RES_SRV, tableName=RESOURCE_SERVER_RESOURCE; dropIndex indexName=IDX_RES_SRV_SCOPE_RES_SRV, tableName=RESOURCE_SERVER_SCOPE		\N	4.25.1	\N	\N	1028395744
authz-3.4.0.CR1-resource-server-pk-change-part3-fixed-nodropindex	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-06-09 19:06:39.055458	48	EXECUTED	9:bdc99e567b3398bac83263d375aad143	addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, tableName=RESOURCE_SERVER_POLICY; addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, tableName=RESOURCE_SERVER_RESOURCE; addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, ...		\N	4.25.1	\N	\N	1028395744
authn-3.4.0.CR1-refresh-token-max-reuse	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-06-09 19:06:39.061716	49	EXECUTED	9:d198654156881c46bfba39abd7769e69	addColumn tableName=REALM		\N	4.25.1	\N	\N	1028395744
3.4.0	keycloak	META-INF/jpa-changelog-3.4.0.xml	2026-06-09 19:06:39.130816	50	EXECUTED	9:cfdd8736332ccdd72c5256ccb42335db	addPrimaryKey constraintName=CONSTRAINT_REALM_DEFAULT_ROLES, tableName=REALM_DEFAULT_ROLES; addPrimaryKey constraintName=CONSTRAINT_COMPOSITE_ROLE, tableName=COMPOSITE_ROLE; addPrimaryKey constraintName=CONSTR_REALM_DEFAULT_GROUPS, tableName=REALM...		\N	4.25.1	\N	\N	1028395744
3.4.0-KEYCLOAK-5230	hmlnarik@redhat.com	META-INF/jpa-changelog-3.4.0.xml	2026-06-09 19:06:39.182174	51	EXECUTED	9:7c84de3d9bd84d7f077607c1a4dcb714	createIndex indexName=IDX_FU_ATTRIBUTE, tableName=FED_USER_ATTRIBUTE; createIndex indexName=IDX_FU_CONSENT, tableName=FED_USER_CONSENT; createIndex indexName=IDX_FU_CONSENT_RU, tableName=FED_USER_CONSENT; createIndex indexName=IDX_FU_CREDENTIAL, t...		\N	4.25.1	\N	\N	1028395744
3.4.1	psilva@redhat.com	META-INF/jpa-changelog-3.4.1.xml	2026-06-09 19:06:39.187353	52	EXECUTED	9:5a6bb36cbefb6a9d6928452c0852af2d	modifyDataType columnName=VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
3.4.2	keycloak	META-INF/jpa-changelog-3.4.2.xml	2026-06-09 19:06:39.191252	53	EXECUTED	9:8f23e334dbc59f82e0a328373ca6ced0	update tableName=REALM		\N	4.25.1	\N	\N	1028395744
3.4.2-KEYCLOAK-5172	mkanis@redhat.com	META-INF/jpa-changelog-3.4.2.xml	2026-06-09 19:06:39.194761	54	EXECUTED	9:9156214268f09d970cdf0e1564d866af	update tableName=CLIENT		\N	4.25.1	\N	\N	1028395744
4.0.0-KEYCLOAK-6335	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-06-09 19:06:39.208035	55	EXECUTED	9:db806613b1ed154826c02610b7dbdf74	createTable tableName=CLIENT_AUTH_FLOW_BINDINGS; addPrimaryKey constraintName=C_CLI_FLOW_BIND, tableName=CLIENT_AUTH_FLOW_BINDINGS		\N	4.25.1	\N	\N	1028395744
4.0.0-CLEANUP-UNUSED-TABLE	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-06-09 19:06:39.218583	56	EXECUTED	9:229a041fb72d5beac76bb94a5fa709de	dropTable tableName=CLIENT_IDENTITY_PROV_MAPPING		\N	4.25.1	\N	\N	1028395744
4.0.0-KEYCLOAK-6228	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-06-09 19:06:39.253706	57	EXECUTED	9:079899dade9c1e683f26b2aa9ca6ff04	dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; dropNotNullConstraint columnName=CLIENT_ID, tableName=USER_CONSENT; addColumn tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHO...		\N	4.25.1	\N	\N	1028395744
4.0.0-KEYCLOAK-5579-fixed	mposolda@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-06-09 19:06:39.425676	58	EXECUTED	9:139b79bcbbfe903bb1c2d2a4dbf001d9	dropForeignKeyConstraint baseTableName=CLIENT_TEMPLATE_ATTRIBUTES, constraintName=FK_CL_TEMPL_ATTR_TEMPL; renameTable newTableName=CLIENT_SCOPE_ATTRIBUTES, oldTableName=CLIENT_TEMPLATE_ATTRIBUTES; renameColumn newColumnName=SCOPE_ID, oldColumnName...		\N	4.25.1	\N	\N	1028395744
authz-4.0.0.CR1	psilva@redhat.com	META-INF/jpa-changelog-authz-4.0.0.CR1.xml	2026-06-09 19:06:39.471301	59	EXECUTED	9:b55738ad889860c625ba2bf483495a04	createTable tableName=RESOURCE_SERVER_PERM_TICKET; addPrimaryKey constraintName=CONSTRAINT_FAPMT, tableName=RESOURCE_SERVER_PERM_TICKET; addForeignKeyConstraint baseTableName=RESOURCE_SERVER_PERM_TICKET, constraintName=FK_FRSRHO213XCX4WNKOG82SSPMT...		\N	4.25.1	\N	\N	1028395744
authz-4.0.0.Beta3	psilva@redhat.com	META-INF/jpa-changelog-authz-4.0.0.Beta3.xml	2026-06-09 19:06:39.481227	60	EXECUTED	9:e0057eac39aa8fc8e09ac6cfa4ae15fe	addColumn tableName=RESOURCE_SERVER_POLICY; addColumn tableName=RESOURCE_SERVER_PERM_TICKET; addForeignKeyConstraint baseTableName=RESOURCE_SERVER_PERM_TICKET, constraintName=FK_FRSRPO2128CX4WNKOG82SSRFY, referencedTableName=RESOURCE_SERVER_POLICY		\N	4.25.1	\N	\N	1028395744
authz-4.2.0.Final	mhajas@redhat.com	META-INF/jpa-changelog-authz-4.2.0.Final.xml	2026-06-09 19:06:39.495088	61	EXECUTED	9:42a33806f3a0443fe0e7feeec821326c	createTable tableName=RESOURCE_URIS; addForeignKeyConstraint baseTableName=RESOURCE_URIS, constraintName=FK_RESOURCE_SERVER_URIS, referencedTableName=RESOURCE_SERVER_RESOURCE; customChange; dropColumn columnName=URI, tableName=RESOURCE_SERVER_RESO...		\N	4.25.1	\N	\N	1028395744
authz-4.2.0.Final-KEYCLOAK-9944	hmlnarik@redhat.com	META-INF/jpa-changelog-authz-4.2.0.Final.xml	2026-06-09 19:06:39.505879	62	EXECUTED	9:9968206fca46eecc1f51db9c024bfe56	addPrimaryKey constraintName=CONSTRAINT_RESOUR_URIS_PK, tableName=RESOURCE_URIS		\N	4.25.1	\N	\N	1028395744
4.2.0-KEYCLOAK-6313	wadahiro@gmail.com	META-INF/jpa-changelog-4.2.0.xml	2026-06-09 19:06:39.512143	63	EXECUTED	9:92143a6daea0a3f3b8f598c97ce55c3d	addColumn tableName=REQUIRED_ACTION_PROVIDER		\N	4.25.1	\N	\N	1028395744
4.3.0-KEYCLOAK-7984	wadahiro@gmail.com	META-INF/jpa-changelog-4.3.0.xml	2026-06-09 19:06:39.516294	64	EXECUTED	9:82bab26a27195d889fb0429003b18f40	update tableName=REQUIRED_ACTION_PROVIDER		\N	4.25.1	\N	\N	1028395744
4.6.0-KEYCLOAK-7950	psilva@redhat.com	META-INF/jpa-changelog-4.6.0.xml	2026-06-09 19:06:39.520213	65	EXECUTED	9:e590c88ddc0b38b0ae4249bbfcb5abc3	update tableName=RESOURCE_SERVER_RESOURCE		\N	4.25.1	\N	\N	1028395744
4.6.0-KEYCLOAK-8377	keycloak	META-INF/jpa-changelog-4.6.0.xml	2026-06-09 19:06:39.542388	66	EXECUTED	9:5c1f475536118dbdc38d5d7977950cc0	createTable tableName=ROLE_ATTRIBUTE; addPrimaryKey constraintName=CONSTRAINT_ROLE_ATTRIBUTE_PK, tableName=ROLE_ATTRIBUTE; addForeignKeyConstraint baseTableName=ROLE_ATTRIBUTE, constraintName=FK_ROLE_ATTRIBUTE_ID, referencedTableName=KEYCLOAK_ROLE...		\N	4.25.1	\N	\N	1028395744
4.6.0-KEYCLOAK-8555	gideonray@gmail.com	META-INF/jpa-changelog-4.6.0.xml	2026-06-09 19:06:39.553286	67	EXECUTED	9:e7c9f5f9c4d67ccbbcc215440c718a17	createIndex indexName=IDX_COMPONENT_PROVIDER_TYPE, tableName=COMPONENT		\N	4.25.1	\N	\N	1028395744
4.7.0-KEYCLOAK-1267	sguilhen@redhat.com	META-INF/jpa-changelog-4.7.0.xml	2026-06-09 19:06:39.56462	68	EXECUTED	9:88e0bfdda924690d6f4e430c53447dd5	addColumn tableName=REALM		\N	4.25.1	\N	\N	1028395744
4.7.0-KEYCLOAK-7275	keycloak	META-INF/jpa-changelog-4.7.0.xml	2026-06-09 19:06:39.591851	69	EXECUTED	9:f53177f137e1c46b6a88c59ec1cb5218	renameColumn newColumnName=CREATED_ON, oldColumnName=LAST_SESSION_REFRESH, tableName=OFFLINE_USER_SESSION; addNotNullConstraint columnName=CREATED_ON, tableName=OFFLINE_USER_SESSION; addColumn tableName=OFFLINE_USER_SESSION; customChange; createIn...		\N	4.25.1	\N	\N	1028395744
4.8.0-KEYCLOAK-8835	sguilhen@redhat.com	META-INF/jpa-changelog-4.8.0.xml	2026-06-09 19:06:39.601652	70	EXECUTED	9:a74d33da4dc42a37ec27121580d1459f	addNotNullConstraint columnName=SSO_MAX_LIFESPAN_REMEMBER_ME, tableName=REALM; addNotNullConstraint columnName=SSO_IDLE_TIMEOUT_REMEMBER_ME, tableName=REALM		\N	4.25.1	\N	\N	1028395744
authz-7.0.0-KEYCLOAK-10443	psilva@redhat.com	META-INF/jpa-changelog-authz-7.0.0.xml	2026-06-09 19:06:39.611074	71	EXECUTED	9:fd4ade7b90c3b67fae0bfcfcb42dfb5f	addColumn tableName=RESOURCE_SERVER		\N	4.25.1	\N	\N	1028395744
8.0.0-adding-credential-columns	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-06-09 19:06:39.627232	72	EXECUTED	9:aa072ad090bbba210d8f18781b8cebf4	addColumn tableName=CREDENTIAL; addColumn tableName=FED_USER_CREDENTIAL		\N	4.25.1	\N	\N	1028395744
8.0.0-updating-credential-data-not-oracle-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-06-09 19:06:39.641024	73	EXECUTED	9:1ae6be29bab7c2aa376f6983b932be37	update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL		\N	4.25.1	\N	\N	1028395744
8.0.0-updating-credential-data-oracle-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-06-09 19:06:39.645165	74	MARK_RAN	9:14706f286953fc9a25286dbd8fb30d97	update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL		\N	4.25.1	\N	\N	1028395744
8.0.0-credential-cleanup-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-06-09 19:06:39.701585	75	EXECUTED	9:2b9cc12779be32c5b40e2e67711a218b	dropDefaultValue columnName=COUNTER, tableName=CREDENTIAL; dropDefaultValue columnName=DIGITS, tableName=CREDENTIAL; dropDefaultValue columnName=PERIOD, tableName=CREDENTIAL; dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; dropColumn ...		\N	4.25.1	\N	\N	1028395744
8.0.0-resource-tag-support	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-06-09 19:06:39.716535	76	EXECUTED	9:91fa186ce7a5af127a2d7a91ee083cc5	addColumn tableName=MIGRATION_MODEL; createIndex indexName=IDX_UPDATE_TIME, tableName=MIGRATION_MODEL		\N	4.25.1	\N	\N	1028395744
9.0.0-always-display-client	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-06-09 19:06:39.725274	77	EXECUTED	9:6335e5c94e83a2639ccd68dd24e2e5ad	addColumn tableName=CLIENT		\N	4.25.1	\N	\N	1028395744
9.0.0-drop-constraints-for-column-increase	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-06-09 19:06:39.728512	78	MARK_RAN	9:6bdb5658951e028bfe16fa0a8228b530	dropUniqueConstraint constraintName=UK_FRSR6T700S9V50BU18WS5PMT, tableName=RESOURCE_SERVER_PERM_TICKET; dropUniqueConstraint constraintName=UK_FRSR6T700S9V50BU18WS5HA6, tableName=RESOURCE_SERVER_RESOURCE; dropPrimaryKey constraintName=CONSTRAINT_O...		\N	4.25.1	\N	\N	1028395744
9.0.0-increase-column-size-federated-fk	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-06-09 19:06:39.78866	79	EXECUTED	9:d5bc15a64117ccad481ce8792d4c608f	modifyDataType columnName=CLIENT_ID, tableName=FED_USER_CONSENT; modifyDataType columnName=CLIENT_REALM_CONSTRAINT, tableName=KEYCLOAK_ROLE; modifyDataType columnName=OWNER, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=CLIENT_ID, ta...		\N	4.25.1	\N	\N	1028395744
9.0.0-recreate-constraints-after-column-increase	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-06-09 19:06:39.792535	80	MARK_RAN	9:077cba51999515f4d3e7ad5619ab592c	addNotNullConstraint columnName=CLIENT_ID, tableName=OFFLINE_CLIENT_SESSION; addNotNullConstraint columnName=OWNER, tableName=RESOURCE_SERVER_PERM_TICKET; addNotNullConstraint columnName=REQUESTER, tableName=RESOURCE_SERVER_PERM_TICKET; addNotNull...		\N	4.25.1	\N	\N	1028395744
9.0.1-add-index-to-client.client_id	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-06-09 19:06:39.807712	81	EXECUTED	9:be969f08a163bf47c6b9e9ead8ac2afb	createIndex indexName=IDX_CLIENT_ID, tableName=CLIENT		\N	4.25.1	\N	\N	1028395744
9.0.1-KEYCLOAK-12579-drop-constraints	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-06-09 19:06:39.811193	82	MARK_RAN	9:6d3bb4408ba5a72f39bd8a0b301ec6e3	dropUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.25.1	\N	\N	1028395744
9.0.1-KEYCLOAK-12579-add-not-null-constraint	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-06-09 19:06:39.820889	83	EXECUTED	9:966bda61e46bebf3cc39518fbed52fa7	addNotNullConstraint columnName=PARENT_GROUP, tableName=KEYCLOAK_GROUP		\N	4.25.1	\N	\N	1028395744
9.0.1-KEYCLOAK-12579-recreate-constraints	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-06-09 19:06:39.823869	84	MARK_RAN	9:8dcac7bdf7378e7d823cdfddebf72fda	addUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.25.1	\N	\N	1028395744
9.0.1-add-index-to-events	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-06-09 19:06:39.837478	85	EXECUTED	9:7d93d602352a30c0c317e6a609b56599	createIndex indexName=IDX_EVENT_TIME, tableName=EVENT_ENTITY		\N	4.25.1	\N	\N	1028395744
map-remove-ri	keycloak	META-INF/jpa-changelog-11.0.0.xml	2026-06-09 19:06:39.854245	86	EXECUTED	9:71c5969e6cdd8d7b6f47cebc86d37627	dropForeignKeyConstraint baseTableName=REALM, constraintName=FK_TRAF444KK6QRKMS7N56AIWQ5Y; dropForeignKeyConstraint baseTableName=KEYCLOAK_ROLE, constraintName=FK_KJHO5LE2C0RAL09FL8CM9WFW9		\N	4.25.1	\N	\N	1028395744
map-remove-ri	keycloak	META-INF/jpa-changelog-12.0.0.xml	2026-06-09 19:06:39.882374	87	EXECUTED	9:a9ba7d47f065f041b7da856a81762021	dropForeignKeyConstraint baseTableName=REALM_DEFAULT_GROUPS, constraintName=FK_DEF_GROUPS_GROUP; dropForeignKeyConstraint baseTableName=REALM_DEFAULT_ROLES, constraintName=FK_H4WPD7W4HSOOLNI3H0SW7BTJE; dropForeignKeyConstraint baseTableName=CLIENT...		\N	4.25.1	\N	\N	1028395744
12.1.0-add-realm-localization-table	keycloak	META-INF/jpa-changelog-12.0.0.xml	2026-06-09 19:06:39.903503	88	EXECUTED	9:fffabce2bc01e1a8f5110d5278500065	createTable tableName=REALM_LOCALIZATIONS; addPrimaryKey tableName=REALM_LOCALIZATIONS		\N	4.25.1	\N	\N	1028395744
default-roles	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:39.919579	89	EXECUTED	9:fa8a5b5445e3857f4b010bafb5009957	addColumn tableName=REALM; customChange		\N	4.25.1	\N	\N	1028395744
default-roles-cleanup	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:39.940881	90	EXECUTED	9:67ac3241df9a8582d591c5ed87125f39	dropTable tableName=REALM_DEFAULT_ROLES; dropTable tableName=CLIENT_DEFAULT_ROLES		\N	4.25.1	\N	\N	1028395744
13.0.0-KEYCLOAK-16844	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:39.954433	91	EXECUTED	9:ad1194d66c937e3ffc82386c050ba089	createIndex indexName=IDX_OFFLINE_USS_PRELOAD, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
map-remove-ri-13.0.0	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:39.983517	92	EXECUTED	9:d9be619d94af5a2f5d07b9f003543b91	dropForeignKeyConstraint baseTableName=DEFAULT_CLIENT_SCOPE, constraintName=FK_R_DEF_CLI_SCOPE_SCOPE; dropForeignKeyConstraint baseTableName=CLIENT_SCOPE_CLIENT, constraintName=FK_C_CLI_SCOPE_SCOPE; dropForeignKeyConstraint baseTableName=CLIENT_SC...		\N	4.25.1	\N	\N	1028395744
13.0.0-KEYCLOAK-17992-drop-constraints	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:39.986471	93	MARK_RAN	9:544d201116a0fcc5a5da0925fbbc3bde	dropPrimaryKey constraintName=C_CLI_SCOPE_BIND, tableName=CLIENT_SCOPE_CLIENT; dropIndex indexName=IDX_CLSCOPE_CL, tableName=CLIENT_SCOPE_CLIENT; dropIndex indexName=IDX_CL_CLSCOPE, tableName=CLIENT_SCOPE_CLIENT		\N	4.25.1	\N	\N	1028395744
13.0.0-increase-column-size-federated	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:40.00974	94	EXECUTED	9:43c0c1055b6761b4b3e89de76d612ccf	modifyDataType columnName=CLIENT_ID, tableName=CLIENT_SCOPE_CLIENT; modifyDataType columnName=SCOPE_ID, tableName=CLIENT_SCOPE_CLIENT		\N	4.25.1	\N	\N	1028395744
13.0.0-KEYCLOAK-17992-recreate-constraints	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:40.013064	95	MARK_RAN	9:8bd711fd0330f4fe980494ca43ab1139	addNotNullConstraint columnName=CLIENT_ID, tableName=CLIENT_SCOPE_CLIENT; addNotNullConstraint columnName=SCOPE_ID, tableName=CLIENT_SCOPE_CLIENT; addPrimaryKey constraintName=C_CLI_SCOPE_BIND, tableName=CLIENT_SCOPE_CLIENT; createIndex indexName=...		\N	4.25.1	\N	\N	1028395744
json-string-accomodation-fixed	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-06-09 19:06:40.028969	96	EXECUTED	9:e07d2bc0970c348bb06fb63b1f82ddbf	addColumn tableName=REALM_ATTRIBUTE; update tableName=REALM_ATTRIBUTE; dropColumn columnName=VALUE, tableName=REALM_ATTRIBUTE; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=REALM_ATTRIBUTE		\N	4.25.1	\N	\N	1028395744
14.0.0-KEYCLOAK-11019	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.061577	97	EXECUTED	9:24fb8611e97f29989bea412aa38d12b7	createIndex indexName=IDX_OFFLINE_CSS_PRELOAD, tableName=OFFLINE_CLIENT_SESSION; createIndex indexName=IDX_OFFLINE_USS_BY_USER, tableName=OFFLINE_USER_SESSION; createIndex indexName=IDX_OFFLINE_USS_BY_USERSESS, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
14.0.0-KEYCLOAK-18286	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.065565	98	MARK_RAN	9:259f89014ce2506ee84740cbf7163aa7	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
14.0.0-KEYCLOAK-18286-revert	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.104544	99	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
14.0.0-KEYCLOAK-18286-supported-dbs	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.122763	100	EXECUTED	9:60ca84a0f8c94ec8c3504a5a3bc88ee8	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
14.0.0-KEYCLOAK-18286-unsupported-dbs	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.127336	101	MARK_RAN	9:d3d977031d431db16e2c181ce49d73e9	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
KEYCLOAK-17267-add-index-to-user-attributes	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.154864	102	EXECUTED	9:0b305d8d1277f3a89a0a53a659ad274c	createIndex indexName=IDX_USER_ATTRIBUTE_NAME, tableName=USER_ATTRIBUTE		\N	4.25.1	\N	\N	1028395744
KEYCLOAK-18146-add-saml-art-binding-identifier	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-06-09 19:06:40.178053	103	EXECUTED	9:2c374ad2cdfe20e2905a84c8fac48460	customChange		\N	4.25.1	\N	\N	1028395744
15.0.0-KEYCLOAK-18467	keycloak	META-INF/jpa-changelog-15.0.0.xml	2026-06-09 19:06:40.200871	104	EXECUTED	9:47a760639ac597360a8219f5b768b4de	addColumn tableName=REALM_LOCALIZATIONS; update tableName=REALM_LOCALIZATIONS; dropColumn columnName=TEXTS, tableName=REALM_LOCALIZATIONS; renameColumn newColumnName=TEXTS, oldColumnName=TEXTS_NEW, tableName=REALM_LOCALIZATIONS; addNotNullConstrai...		\N	4.25.1	\N	\N	1028395744
17.0.0-9562	keycloak	META-INF/jpa-changelog-17.0.0.xml	2026-06-09 19:06:40.225847	105	EXECUTED	9:a6272f0576727dd8cad2522335f5d99e	createIndex indexName=IDX_USER_SERVICE_ACCOUNT, tableName=USER_ENTITY		\N	4.25.1	\N	\N	1028395744
18.0.0-10625-IDX_ADMIN_EVENT_TIME	keycloak	META-INF/jpa-changelog-18.0.0.xml	2026-06-09 19:06:40.243519	106	EXECUTED	9:015479dbd691d9cc8669282f4828c41d	createIndex indexName=IDX_ADMIN_EVENT_TIME, tableName=ADMIN_EVENT_ENTITY		\N	4.25.1	\N	\N	1028395744
18.0.15-30992-index-consent	keycloak	META-INF/jpa-changelog-18.0.15.xml	2026-06-09 19:06:40.273441	107	EXECUTED	9:80071ede7a05604b1f4906f3bf3b00f0	createIndex indexName=IDX_USCONSENT_SCOPE_ID, tableName=USER_CONSENT_CLIENT_SCOPE		\N	4.25.1	\N	\N	1028395744
19.0.0-10135	keycloak	META-INF/jpa-changelog-19.0.0.xml	2026-06-09 19:06:40.296613	108	EXECUTED	9:9518e495fdd22f78ad6425cc30630221	customChange		\N	4.25.1	\N	\N	1028395744
20.0.0-12964-supported-dbs	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-06-09 19:06:40.310054	109	EXECUTED	9:e5f243877199fd96bcc842f27a1656ac	createIndex indexName=IDX_GROUP_ATT_BY_NAME_VALUE, tableName=GROUP_ATTRIBUTE		\N	4.25.1	\N	\N	1028395744
20.0.0-12964-unsupported-dbs	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-06-09 19:06:40.313102	110	MARK_RAN	9:1a6fcaa85e20bdeae0a9ce49b41946a5	createIndex indexName=IDX_GROUP_ATT_BY_NAME_VALUE, tableName=GROUP_ATTRIBUTE		\N	4.25.1	\N	\N	1028395744
client-attributes-string-accomodation-fixed	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-06-09 19:06:40.325586	111	EXECUTED	9:3f332e13e90739ed0c35b0b25b7822ca	addColumn tableName=CLIENT_ATTRIBUTES; update tableName=CLIENT_ATTRIBUTES; dropColumn columnName=VALUE, tableName=CLIENT_ATTRIBUTES; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
21.0.2-17277	keycloak	META-INF/jpa-changelog-21.0.2.xml	2026-06-09 19:06:40.336415	112	EXECUTED	9:7ee1f7a3fb8f5588f171fb9a6ab623c0	customChange		\N	4.25.1	\N	\N	1028395744
21.1.0-19404	keycloak	META-INF/jpa-changelog-21.1.0.xml	2026-06-09 19:06:40.392749	113	EXECUTED	9:3d7e830b52f33676b9d64f7f2b2ea634	modifyDataType columnName=DECISION_STRATEGY, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=LOGIC, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=POLICY_ENFORCE_MODE, tableName=RESOURCE_SERVER		\N	4.25.1	\N	\N	1028395744
21.1.0-19404-2	keycloak	META-INF/jpa-changelog-21.1.0.xml	2026-06-09 19:06:40.397937	114	MARK_RAN	9:627d032e3ef2c06c0e1f73d2ae25c26c	addColumn tableName=RESOURCE_SERVER_POLICY; update tableName=RESOURCE_SERVER_POLICY; dropColumn columnName=DECISION_STRATEGY, tableName=RESOURCE_SERVER_POLICY; renameColumn newColumnName=DECISION_STRATEGY, oldColumnName=DECISION_STRATEGY_NEW, tabl...		\N	4.25.1	\N	\N	1028395744
22.0.0-17484-updated	keycloak	META-INF/jpa-changelog-22.0.0.xml	2026-06-09 19:06:40.410529	115	EXECUTED	9:90af0bfd30cafc17b9f4d6eccd92b8b3	customChange		\N	4.25.1	\N	\N	1028395744
22.0.5-24031	keycloak	META-INF/jpa-changelog-22.0.0.xml	2026-06-09 19:06:40.414152	116	MARK_RAN	9:a60d2d7b315ec2d3eba9e2f145f9df28	customChange		\N	4.25.1	\N	\N	1028395744
23.0.0-12062	keycloak	META-INF/jpa-changelog-23.0.0.xml	2026-06-09 19:06:40.428001	117	EXECUTED	9:2168fbe728fec46ae9baf15bf80927b8	addColumn tableName=COMPONENT_CONFIG; update tableName=COMPONENT_CONFIG; dropColumn columnName=VALUE, tableName=COMPONENT_CONFIG; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=COMPONENT_CONFIG		\N	4.25.1	\N	\N	1028395744
23.0.0-17258	keycloak	META-INF/jpa-changelog-23.0.0.xml	2026-06-09 19:06:40.435536	118	EXECUTED	9:36506d679a83bbfda85a27ea1864dca8	addColumn tableName=EVENT_ENTITY		\N	4.25.1	\N	\N	1028395744
24.0.0-9758	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-06-09 19:06:40.478149	119	EXECUTED	9:502c557a5189f600f0f445a9b49ebbce	addColumn tableName=USER_ATTRIBUTE; addColumn tableName=FED_USER_ATTRIBUTE; createIndex indexName=USER_ATTR_LONG_VALUES, tableName=USER_ATTRIBUTE; createIndex indexName=FED_USER_ATTR_LONG_VALUES, tableName=FED_USER_ATTRIBUTE; createIndex indexName...		\N	4.25.1	\N	\N	1028395744
24.0.0-9758-2	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-06-09 19:06:40.490906	120	EXECUTED	9:bf0fdee10afdf597a987adbf291db7b2	customChange		\N	4.25.1	\N	\N	1028395744
24.0.0-26618-drop-index-if-present	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-06-09 19:06:40.503978	121	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
24.0.0-26618-reindex	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-06-09 19:06:40.519435	122	EXECUTED	9:08707c0f0db1cef6b352db03a60edc7f	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
24.0.2-27228	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-06-09 19:06:40.533888	123	EXECUTED	9:eaee11f6b8aa25d2cc6a84fb86fc6238	customChange		\N	4.25.1	\N	\N	1028395744
24.0.2-27967-drop-index-if-present	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-06-09 19:06:40.537854	124	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
24.0.2-27967-reindex	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-06-09 19:06:40.542323	125	MARK_RAN	9:d3d977031d431db16e2c181ce49d73e9	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.25.1	\N	\N	1028395744
25.0.0-28265-tables	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.555395	126	EXECUTED	9:deda2df035df23388af95bbd36c17cef	addColumn tableName=OFFLINE_USER_SESSION; addColumn tableName=OFFLINE_CLIENT_SESSION		\N	4.25.1	\N	\N	1028395744
25.0.0-28265-index-creation	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.567011	127	EXECUTED	9:3e96709818458ae49f3c679ae58d263a	createIndex indexName=IDX_OFFLINE_USS_BY_LAST_SESSION_REFRESH, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
25.0.0-28265-index-cleanup	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.579802	128	EXECUTED	9:8c0cfa341a0474385b324f5c4b2dfcc1	dropIndex indexName=IDX_OFFLINE_USS_CREATEDON, tableName=OFFLINE_USER_SESSION; dropIndex indexName=IDX_OFFLINE_USS_PRELOAD, tableName=OFFLINE_USER_SESSION; dropIndex indexName=IDX_OFFLINE_USS_BY_USERSESS, tableName=OFFLINE_USER_SESSION; dropIndex ...		\N	4.25.1	\N	\N	1028395744
25.0.0-28265-index-2-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.583718	129	MARK_RAN	9:b7ef76036d3126bb83c2423bf4d449d6	createIndex indexName=IDX_OFFLINE_USS_BY_BROKER_SESSION_ID, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
25.0.0-28265-index-2-not-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.596703	130	EXECUTED	9:23396cf51ab8bc1ae6f0cac7f9f6fcf7	createIndex indexName=IDX_OFFLINE_USS_BY_BROKER_SESSION_ID, tableName=OFFLINE_USER_SESSION		\N	4.25.1	\N	\N	1028395744
25.0.0-org	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.652168	131	EXECUTED	9:5c859965c2c9b9c72136c360649af157	createTable tableName=ORG; addUniqueConstraint constraintName=UK_ORG_NAME, tableName=ORG; addUniqueConstraint constraintName=UK_ORG_GROUP, tableName=ORG; createTable tableName=ORG_DOMAIN		\N	4.25.1	\N	\N	1028395744
unique-consentuser	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.688196	132	EXECUTED	9:5857626a2ea8767e9a6c66bf3a2cb32f	customChange; dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_LOCAL_CONSENT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_EXTERNAL_CONSENT, tableName=...		\N	4.25.1	\N	\N	1028395744
unique-consentuser-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.692704	133	MARK_RAN	9:b79478aad5adaa1bc428e31563f55e8e	customChange; dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_LOCAL_CONSENT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_EXTERNAL_CONSENT, tableName=...		\N	4.25.1	\N	\N	1028395744
25.0.0-28861-index-creation	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-06-09 19:06:40.714131	134	EXECUTED	9:b9acb58ac958d9ada0fe12a5d4794ab1	createIndex indexName=IDX_PERM_TICKET_REQUESTER, tableName=RESOURCE_SERVER_PERM_TICKET; createIndex indexName=IDX_PERM_TICKET_OWNER, tableName=RESOURCE_SERVER_PERM_TICKET		\N	4.25.1	\N	\N	1028395744
\.


--
-- Data for Name: databasechangeloglock; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.databasechangeloglock (id, locked, lockgranted, lockedby) FROM stdin;
1	f	\N	\N
1000	f	\N	\N
\.


--
-- Data for Name: default_client_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.default_client_scope (realm_id, scope_id, default_scope) FROM stdin;
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	e7de7027-5f94-4eea-a86e-1b709749eb45	f
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	d0eb9230-68b8-4071-869b-377240dbde1f	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	fa3301c7-ea7f-4983-a85e-999570232089	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	37310c78-d1fd-4cfe-82b4-e94501f869e2	f
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	dff4c9c5-910a-4f48-ab2f-9819daddeba7	f
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	0fe1ad1b-d18e-47af-ae41-84830d69a087	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	b996718d-07af-4a21-a55f-4725e56f65d6	f
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	cffaa3e2-535b-4f21-aea4-acfe9a01727f	t
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	376ff0c4-cf97-4d39-bcfb-b3c20e837898	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	05563931-429a-4f06-8e68-5dca524f810f	f
6a264182-ab2b-4da7-a868-c7dddf4329f2	bcffc1cd-2dd6-4a6d-9b98-9adddf1990d2	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	9909b566-87fd-4c63-a73d-9bdbd519d20f	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	b6128b6c-a696-4741-ae21-17d2141078a2	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed	f
6a264182-ab2b-4da7-a868-c7dddf4329f2	bb96564a-5296-4a0b-973c-d7d57122fa10	f
6a264182-ab2b-4da7-a868-c7dddf4329f2	214d076c-cb63-47fd-867b-0686d3bea7bd	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	9cbc56ff-df36-4b4b-884d-e98732737867	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	8fa29864-971f-4c81-9d21-12aaea3be7dd	f
6a264182-ab2b-4da7-a868-c7dddf4329f2	fb3d66d0-362f-4feb-a772-3c8a81766f8c	t
6a264182-ab2b-4da7-a868-c7dddf4329f2	ba724387-db2e-430a-879b-6ec46f406df2	t
\.


--
-- Data for Name: event_entity; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.event_entity (id, client_id, details_json, error, ip_address, realm_id, session_id, event_time, type, user_id, details_json_long_value) FROM stdin;
\.


--
-- Data for Name: fed_user_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_attribute (id, name, user_id, realm_id, storage_provider_id, value, long_value_hash, long_value_hash_lower_case, long_value) FROM stdin;
\.


--
-- Data for Name: fed_user_consent; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_consent (id, client_id, user_id, realm_id, storage_provider_id, created_date, last_updated_date, client_storage_provider, external_client_id) FROM stdin;
\.


--
-- Data for Name: fed_user_consent_cl_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_consent_cl_scope (user_consent_id, scope_id) FROM stdin;
\.


--
-- Data for Name: fed_user_credential; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_credential (id, salt, type, created_date, user_id, realm_id, storage_provider_id, user_label, secret_data, credential_data, priority) FROM stdin;
\.


--
-- Data for Name: fed_user_group_membership; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_group_membership (group_id, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: fed_user_required_action; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_required_action (required_action, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: fed_user_role_mapping; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.fed_user_role_mapping (role_id, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: federated_identity; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.federated_identity (identity_provider, realm_id, federated_user_id, federated_username, token, user_id) FROM stdin;
\.


--
-- Data for Name: federated_user; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.federated_user (id, storage_provider_id, realm_id) FROM stdin;
\.


--
-- Data for Name: group_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.group_attribute (id, name, value, group_id) FROM stdin;
\.


--
-- Data for Name: group_role_mapping; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.group_role_mapping (role_id, group_id) FROM stdin;
\.


--
-- Data for Name: identity_provider; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.identity_provider (internal_id, enabled, provider_alias, provider_id, store_token, authenticate_by_default, realm_id, add_token_role, trust_email, first_broker_login_flow_id, post_broker_login_flow_id, provider_display_name, link_only) FROM stdin;
\.


--
-- Data for Name: identity_provider_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.identity_provider_config (identity_provider_id, value, name) FROM stdin;
\.


--
-- Data for Name: identity_provider_mapper; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.identity_provider_mapper (id, name, idp_alias, idp_mapper_name, realm_id) FROM stdin;
\.


--
-- Data for Name: idp_mapper_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.idp_mapper_config (idp_mapper_id, value, name) FROM stdin;
\.


--
-- Data for Name: keycloak_group; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.keycloak_group (id, name, parent_group, realm_id) FROM stdin;
\.


--
-- Data for Name: keycloak_role; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.keycloak_role (id, client_realm_constraint, client_role, description, name, realm_id, client, realm) FROM stdin;
c5f92874-1f2c-42cf-ad4f-a4ccf962cce9	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	${role_default-roles}	default-roles-master	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	\N
34dce5e6-6ea9-46fe-949d-b86e27d16341	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	${role_create-realm}	create-realm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	\N
bdc9e819-5bbe-4f18-8e7a-2931aaacda7c	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	${role_admin}	admin	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	\N
caa0ec3a-5274-4a30-b462-4d3db7775a3f	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_create-client}	create-client	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
db4d346a-a1e7-484d-adae-4654608933a2	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-realm}	view-realm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
8cddcfc9-3959-4561-b59a-c5d401cbbb8e	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-users}	view-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
e5b0777e-dee7-44d6-b419-cd7d56d73996	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-clients}	view-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
e58a23ef-dfca-48eb-84f8-916f17c8698e	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-events}	view-events	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
d628ca16-19e4-47d5-b5e0-7bce7e2b0533	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-identity-providers}	view-identity-providers	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
839416e9-e124-4009-857e-1e31bcf0b656	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_view-authorization}	view-authorization	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
2937775c-79df-4924-b2bd-b4316b0a0d61	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-realm}	manage-realm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
547a68c0-9a7a-4f48-81eb-a4d62cee05b1	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-users}	manage-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
42a3f5d8-bd3e-41a8-872f-c7fcc0ca31f6	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-clients}	manage-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
15522bbd-c298-42c3-b2a5-f6da7ce842ee	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-events}	manage-events	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
b5cf9f07-6c41-464b-b26b-da8899f73dc5	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-identity-providers}	manage-identity-providers	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
7c325b53-f20c-474a-a75d-f2176cb6207c	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_manage-authorization}	manage-authorization	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
5a3c68ed-bd91-4e44-afae-2999760b7006	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_query-users}	query-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
5c509666-cb36-4d3e-a11f-bde89c621284	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_query-clients}	query-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
7f273eb2-8d47-43b2-b69f-f2ea5b202eff	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_query-realms}	query-realms	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
e4ee5423-abc5-45bd-a2c0-151c32ae38da	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_query-groups}	query-groups	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
063594c3-5561-4859-a81f-610e32b50a4a	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_view-profile}	view-profile	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
ff571d5a-d56e-4937-a412-60049b740c33	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_manage-account}	manage-account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
1a983def-3178-4b56-882b-2204f99d96d8	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_manage-account-links}	manage-account-links	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
c1f7e365-2136-4f6f-a4fc-fb8f2e813b3b	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_view-applications}	view-applications	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
42c2533c-2344-4f58-a033-d7bfa6a0b05d	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_view-consent}	view-consent	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
86d0901e-138f-478e-96ce-d6336bbda074	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_manage-consent}	manage-consent	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
e271e581-191e-4d66-ad3d-f5dcf02742ac	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_view-groups}	view-groups	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
481cf818-9dad-4777-ba14-36a3000288a6	28a13f19-a581-48cf-9d27-203c80b5be3a	t	${role_delete-account}	delete-account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	28a13f19-a581-48cf-9d27-203c80b5be3a	\N
117ffc8a-0f6a-4276-9ac6-057be5850701	f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	t	${role_read-token}	read-token	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f1953c6c-c515-4bc4-8ba8-e6b4873e3dd1	\N
b42c747d-9b0e-4bc3-b301-d89c739e68b9	25a276e3-07eb-49e9-86a9-5a15a5f09800	t	${role_impersonation}	impersonation	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	25a276e3-07eb-49e9-86a9-5a15a5f09800	\N
f751e3a5-e8da-4298-aa6b-38d8cc932fe5	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	${role_offline-access}	offline_access	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	\N
6fb9fb79-6498-4795-a21a-f5d24981ed62	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	${role_uma_authorization}	uma_authorization	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	\N	\N
c2043b06-2175-4019-89aa-9bef1b881b62	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	${role_default-roles}	default-roles-pulse	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
1c065dd1-d8bc-46ef-90f3-6fedc4fdf66f	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_create-client}	create-client	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
61a7e7c7-1c19-4526-9260-d05be634dd75	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-realm}	view-realm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
34d1863f-a724-4c37-90ea-ad092406e8d6	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-users}	view-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
157a1a8c-2149-4992-aa7e-7c361a6739fe	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-clients}	view-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
e94828cf-57a3-4b7a-81eb-6025470c7845	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-events}	view-events	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
44d1147b-6188-4de4-ae4a-c56079aeb97b	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-identity-providers}	view-identity-providers	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
e1ea24c2-f5e4-44da-a7ef-a5be328c756b	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_view-authorization}	view-authorization	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
409da1da-bc78-41e9-aba9-829be59fd9b0	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-realm}	manage-realm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
128059cd-7f66-4548-bc02-0112423760fc	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-users}	manage-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
7dfed9d9-ff07-4bb5-9198-3fc70d8be076	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-clients}	manage-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
2abe3551-dcde-44d2-bb41-2c6b43f2546f	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-events}	manage-events	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
f2edb580-16f3-40b6-a092-c1aeb72198b7	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-identity-providers}	manage-identity-providers	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
7fe7cbd9-ab4f-4412-808d-f96a601bde33	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_manage-authorization}	manage-authorization	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
3fa0b7ab-ebe7-457a-97d7-3636cd9b499f	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_query-users}	query-users	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
f6d7a6a9-6d79-4720-9534-f4d90ef8a068	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_query-clients}	query-clients	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
8bad5d61-5fea-4525-9285-71bd5809461f	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_query-realms}	query-realms	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
9fb820f1-8447-4d42-bfdb-1c984a6e54c5	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_query-groups}	query-groups	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
be040f8a-b2ed-460e-abd8-8c1e9ea8e25f	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_realm-admin}	realm-admin	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
6d6f1ff4-f643-46c0-a6f1-e48e11671362	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_create-client}	create-client	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
3d4db894-de9f-493d-a50f-bba47b85039e	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-realm}	view-realm	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
7e098030-d97b-4651-82f4-3a3c3e60d097	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-users}	view-users	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
6ea0f2d5-da8b-4789-88ed-c87b99c2d896	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-clients}	view-clients	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
b5c2b21d-cba4-455d-8fd3-2d005ac9dfbf	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-events}	view-events	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
f21ebbfa-9d0e-4cb3-a85f-c3a116ec5d75	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-identity-providers}	view-identity-providers	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
de98959e-7cb0-4d63-8e73-b49672048e63	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_view-authorization}	view-authorization	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
0f86459f-3f47-45ab-b493-909b1852fb03	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-realm}	manage-realm	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
a0ad5d4c-03eb-4226-8366-d076aaff720c	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-users}	manage-users	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
998df5d5-3e15-4f15-adca-c971c96a5aaf	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-clients}	manage-clients	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
8de0c1b1-27a3-4aef-b625-2d4778e70238	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-events}	manage-events	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
4d5886b4-432e-488b-aed1-89631c8993ef	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-identity-providers}	manage-identity-providers	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
1f47328a-3a1f-4219-aad5-924aaa302317	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_manage-authorization}	manage-authorization	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
4b76e09c-26d0-40e4-8c69-9c9a10339f3e	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_query-users}	query-users	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
de7df76b-ca64-4d61-887b-28df10251711	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_query-clients}	query-clients	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
c317a900-d921-4688-b259-eb5fcb3e20a0	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_query-realms}	query-realms	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
a34344e7-5369-49c1-971a-91a858989f43	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_query-groups}	query-groups	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
22da8887-f53f-4429-ab44-e535258762ed	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_view-profile}	view-profile	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
f53862a5-f9b3-462e-ba32-cfccb6990d3a	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_manage-account}	manage-account	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
5275d222-efc0-4f67-af4d-a4ac35765e92	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_manage-account-links}	manage-account-links	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
2d8f1f8c-1227-47d9-ab65-346ae680eb89	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_view-applications}	view-applications	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
2c1cf615-6530-4c98-b689-66530eda52a5	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_view-consent}	view-consent	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
c2a6016a-7963-4854-9023-45d491ab5ba1	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_manage-consent}	manage-consent	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
a2640def-7dff-496a-af38-d7ec3b7f71f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_view-groups}	view-groups	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
5c336f80-1d3d-46a7-a811-3203665d0532	6d6f00fd-79c0-4acc-a3de-b28063ec0926	t	${role_delete-account}	delete-account	6a264182-ab2b-4da7-a868-c7dddf4329f2	6d6f00fd-79c0-4acc-a3de-b28063ec0926	\N
eec11496-53b0-45e4-9704-17703d316efb	724428c1-ccb1-4367-87f8-64d2d37295e8	t	${role_impersonation}	impersonation	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	724428c1-ccb1-4367-87f8-64d2d37295e8	\N
6545e5cd-6529-407d-8801-56e8ed73120a	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	t	${role_impersonation}	impersonation	6a264182-ab2b-4da7-a868-c7dddf4329f2	8dec21bc-3dcc-4aff-8c3a-efa74fef5914	\N
baca9f64-e31e-497d-a191-adcd557cf083	3c612010-d61f-4061-adb1-a09a4b7c2a51	t	${role_read-token}	read-token	6a264182-ab2b-4da7-a868-c7dddf4329f2	3c612010-d61f-4061-adb1-a09a4b7c2a51	\N
881460b5-a8c5-496f-a49d-827b4abccdc6	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	${role_offline-access}	offline_access	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
3ed27b29-842c-45e8-85d1-86dc1e8352ea	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	Collaborateur - accès basique RH	collaborator	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
3aab11c8-d1af-418d-8140-934edbed7206	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	Manager - KPIs équipe et alertes	manager	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
6d9dfee5-4172-4cd2-b3f5-417c22c75afd	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	Équipe RH - gestion complète	hr	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
73110a6c-ba2b-46d9-9f9b-c1368ad2a36f	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	Direction - tableaux de bord stratégiques	director	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
614d7bf5-0662-47f4-83af-168466e0c362	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	Administrateur technique - accès total	admin	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
a302631e-097f-4ef2-b3d0-7f682a1b6979	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	${role_uma_authorization}	uma_authorization	6a264182-ab2b-4da7-a868-c7dddf4329f2	\N	\N
\.


--
-- Data for Name: migration_model; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.migration_model (id, version, update_time) FROM stdin;
hte0s	25.0.6	1781028401
\.


--
-- Data for Name: offline_client_session; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.offline_client_session (user_session_id, client_id, offline_flag, "timestamp", data, client_storage_provider, external_client_id, version) FROM stdin;
\.


--
-- Data for Name: offline_user_session; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.offline_user_session (user_session_id, user_id, realm_id, created_on, offline_flag, data, last_session_refresh, broker_session_id, version) FROM stdin;
\.


--
-- Data for Name: org; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.org (id, enabled, realm_id, group_id, name, description) FROM stdin;
\.


--
-- Data for Name: org_domain; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.org_domain (id, name, verified, org_id) FROM stdin;
\.


--
-- Data for Name: policy_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.policy_config (policy_id, name, value) FROM stdin;
\.


--
-- Data for Name: protocol_mapper; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.protocol_mapper (id, name, protocol, protocol_mapper_name, client_id, client_scope_id) FROM stdin;
18d7f868-29e3-471f-98ab-72ea772e1620	audience resolve	openid-connect	oidc-audience-resolve-mapper	2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	\N
9454ff01-4951-4301-853e-9be8edf811b0	locale	openid-connect	oidc-usermodel-attribute-mapper	c9127146-5188-4383-bc83-8371c445ed88	\N
d57f5e2c-157e-48e5-b13b-b8f376b7a0bf	role list	saml	saml-role-list-mapper	\N	d0eb9230-68b8-4071-869b-377240dbde1f
b393d3f1-525d-4cd5-b509-966538547667	full name	openid-connect	oidc-full-name-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
f47b4172-1953-44a7-83a7-7415e74bd594	family name	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
77a7538a-fc79-4214-b2f8-c3fe95363ceb	given name	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
b7e8eec6-483b-4321-9844-f11fc09ed7d4	middle name	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
d0849a4e-c639-4346-be34-03ef2628ff60	nickname	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	username	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
13a6e15a-37ed-47a3-a616-b3052c038185	profile	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	picture	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
199f43c3-6824-404d-9270-f555c3a4677a	website	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
507c7984-58ff-4065-b724-6fda82df8a50	gender	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	birthdate	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	zoneinfo	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
fe0545e6-98f9-48dd-ad25-bde381fcb03c	locale	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
14d169d3-8248-4c78-85d6-e482b7373a1d	updated at	openid-connect	oidc-usermodel-attribute-mapper	\N	3d6416d8-9d5c-4f05-a1ae-24cfb7589cf6
06f5ad90-70f7-47c3-8020-526fa4f67321	email	openid-connect	oidc-usermodel-attribute-mapper	\N	fa3301c7-ea7f-4983-a85e-999570232089
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	email verified	openid-connect	oidc-usermodel-property-mapper	\N	fa3301c7-ea7f-4983-a85e-999570232089
5ba88915-aa83-457d-8da5-b5be006c4b09	address	openid-connect	oidc-address-mapper	\N	37310c78-d1fd-4cfe-82b4-e94501f869e2
15f64c34-bdfd-40fe-92e4-67d73056ee80	phone number	openid-connect	oidc-usermodel-attribute-mapper	\N	dff4c9c5-910a-4f48-ab2f-9819daddeba7
a819e220-7d82-4d58-8ef5-a837fb318239	phone number verified	openid-connect	oidc-usermodel-attribute-mapper	\N	dff4c9c5-910a-4f48-ab2f-9819daddeba7
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	realm roles	openid-connect	oidc-usermodel-realm-role-mapper	\N	0fe1ad1b-d18e-47af-ae41-84830d69a087
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	client roles	openid-connect	oidc-usermodel-client-role-mapper	\N	0fe1ad1b-d18e-47af-ae41-84830d69a087
e6d7361d-d8d0-406c-a481-5a4ebf8ea2c6	audience resolve	openid-connect	oidc-audience-resolve-mapper	\N	0fe1ad1b-d18e-47af-ae41-84830d69a087
d4b1c12c-db26-46ee-9683-d2fd476aaa69	allowed web origins	openid-connect	oidc-allowed-origins-mapper	\N	6fbba32f-5d72-4e39-9f4a-69b0dfb60bcf
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	upn	openid-connect	oidc-usermodel-attribute-mapper	\N	b996718d-07af-4a21-a55f-4725e56f65d6
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	groups	openid-connect	oidc-usermodel-realm-role-mapper	\N	b996718d-07af-4a21-a55f-4725e56f65d6
508693ad-b1b7-40fd-ad54-20ec2fa369c1	acr loa level	openid-connect	oidc-acr-mapper	\N	cffaa3e2-535b-4f21-aea4-acfe9a01727f
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	auth_time	openid-connect	oidc-usersessionmodel-note-mapper	\N	376ff0c4-cf97-4d39-bcfb-b3c20e837898
14900a52-4f03-48f3-a68c-4eb6715c8196	sub	openid-connect	oidc-sub-mapper	\N	376ff0c4-cf97-4d39-bcfb-b3c20e837898
cf6aa1f1-0db2-4c4f-beab-dfd9348722b4	audience resolve	openid-connect	oidc-audience-resolve-mapper	d2e77719-c7fa-48e1-9d93-95b5f409862a	\N
68575c42-31c9-4dd0-a2a3-ebcfde131db6	role list	saml	saml-role-list-mapper	\N	bcffc1cd-2dd6-4a6d-9b98-9adddf1990d2
21f1e2f7-d02a-4602-9f63-135d8decf653	full name	openid-connect	oidc-full-name-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
10ca056c-cef6-4535-ab57-1201c7db2f8a	family name	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
399839c9-4d48-419f-a6d1-692b74120ce7	given name	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
c4def597-fca6-47bc-a5da-a47990da02da	middle name	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	nickname	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
23fc83d5-32ef-40e1-b240-ec5d6101f37c	username	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	profile	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
a304d0a2-bdcb-4307-a485-bb21c17a68f2	picture	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
86c4958c-ee18-4b65-917c-0632759d87b4	website	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	gender	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	birthdate	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	zoneinfo	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
ab7f1e8a-add2-4ce1-a398-41465669f0c2	locale	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
48b57352-be17-4053-8156-97e13a1127df	updated at	openid-connect	oidc-usermodel-attribute-mapper	\N	9909b566-87fd-4c63-a73d-9bdbd519d20f
44f9792e-6948-4c5f-bc7a-6b79396de006	email	openid-connect	oidc-usermodel-attribute-mapper	\N	b6128b6c-a696-4741-ae21-17d2141078a2
014e1483-9907-4925-a967-ad8db6194b18	email verified	openid-connect	oidc-usermodel-property-mapper	\N	b6128b6c-a696-4741-ae21-17d2141078a2
baf54769-b86d-46ae-abb8-e9be7e344881	address	openid-connect	oidc-address-mapper	\N	f3a7dd1e-7ce5-44a1-b398-16b3b7a1b1ed
337427b0-248a-4d62-8b4a-71c705e03a06	phone number	openid-connect	oidc-usermodel-attribute-mapper	\N	bb96564a-5296-4a0b-973c-d7d57122fa10
d567fc4c-5db9-49e4-b36e-bf092953cd75	phone number verified	openid-connect	oidc-usermodel-attribute-mapper	\N	bb96564a-5296-4a0b-973c-d7d57122fa10
35ca1a32-edd5-40cc-af4a-0565e6797abc	realm roles	openid-connect	oidc-usermodel-realm-role-mapper	\N	214d076c-cb63-47fd-867b-0686d3bea7bd
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	client roles	openid-connect	oidc-usermodel-client-role-mapper	\N	214d076c-cb63-47fd-867b-0686d3bea7bd
7362e0d7-227e-4944-8ff9-39a8bfeef0e4	audience resolve	openid-connect	oidc-audience-resolve-mapper	\N	214d076c-cb63-47fd-867b-0686d3bea7bd
c96b3fc3-a9b5-44d4-8bb9-70f41adcce89	allowed web origins	openid-connect	oidc-allowed-origins-mapper	\N	9cbc56ff-df36-4b4b-884d-e98732737867
afbf0361-f65a-43ed-a1e0-430b7f3288e7	upn	openid-connect	oidc-usermodel-attribute-mapper	\N	8fa29864-971f-4c81-9d21-12aaea3be7dd
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	groups	openid-connect	oidc-usermodel-realm-role-mapper	\N	8fa29864-971f-4c81-9d21-12aaea3be7dd
808283b3-4553-4413-9dd5-d97ddb9cfb57	acr loa level	openid-connect	oidc-acr-mapper	\N	fb3d66d0-362f-4feb-a772-3c8a81766f8c
a15e9e6f-c939-4818-b1c5-315139640583	auth_time	openid-connect	oidc-usersessionmodel-note-mapper	\N	ba724387-db2e-430a-879b-6ec46f406df2
adc4fd89-a051-4265-bf9f-7964703140c5	sub	openid-connect	oidc-sub-mapper	\N	ba724387-db2e-430a-879b-6ec46f406df2
73b580aa-54ba-4c4a-9b84-5663fd326daa	Client ID	openid-connect	oidc-usersessionmodel-note-mapper	710ee357-9495-4b0b-8f44-907835d002b3	\N
18f602f7-005d-4424-a5b5-4018fb921645	Client Host	openid-connect	oidc-usersessionmodel-note-mapper	710ee357-9495-4b0b-8f44-907835d002b3	\N
0364520e-6da8-4bec-ac91-73266daa1e71	Client IP Address	openid-connect	oidc-usersessionmodel-note-mapper	710ee357-9495-4b0b-8f44-907835d002b3	\N
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	locale	openid-connect	oidc-usermodel-attribute-mapper	94b40267-f844-4f8e-996e-3bc5b0800c08	\N
\.


--
-- Data for Name: protocol_mapper_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.protocol_mapper_config (protocol_mapper_id, value, name) FROM stdin;
9454ff01-4951-4301-853e-9be8edf811b0	true	introspection.token.claim
9454ff01-4951-4301-853e-9be8edf811b0	true	userinfo.token.claim
9454ff01-4951-4301-853e-9be8edf811b0	locale	user.attribute
9454ff01-4951-4301-853e-9be8edf811b0	true	id.token.claim
9454ff01-4951-4301-853e-9be8edf811b0	true	access.token.claim
9454ff01-4951-4301-853e-9be8edf811b0	locale	claim.name
9454ff01-4951-4301-853e-9be8edf811b0	String	jsonType.label
d57f5e2c-157e-48e5-b13b-b8f376b7a0bf	false	single
d57f5e2c-157e-48e5-b13b-b8f376b7a0bf	Basic	attribute.nameformat
d57f5e2c-157e-48e5-b13b-b8f376b7a0bf	Role	attribute.name
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	true	introspection.token.claim
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	true	userinfo.token.claim
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	zoneinfo	user.attribute
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	true	id.token.claim
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	true	access.token.claim
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	zoneinfo	claim.name
078f6f1d-82dd-44a3-8db0-cb8bce0ade77	String	jsonType.label
13a6e15a-37ed-47a3-a616-b3052c038185	true	introspection.token.claim
13a6e15a-37ed-47a3-a616-b3052c038185	true	userinfo.token.claim
13a6e15a-37ed-47a3-a616-b3052c038185	profile	user.attribute
13a6e15a-37ed-47a3-a616-b3052c038185	true	id.token.claim
13a6e15a-37ed-47a3-a616-b3052c038185	true	access.token.claim
13a6e15a-37ed-47a3-a616-b3052c038185	profile	claim.name
13a6e15a-37ed-47a3-a616-b3052c038185	String	jsonType.label
14d169d3-8248-4c78-85d6-e482b7373a1d	true	introspection.token.claim
14d169d3-8248-4c78-85d6-e482b7373a1d	true	userinfo.token.claim
14d169d3-8248-4c78-85d6-e482b7373a1d	updatedAt	user.attribute
14d169d3-8248-4c78-85d6-e482b7373a1d	true	id.token.claim
14d169d3-8248-4c78-85d6-e482b7373a1d	true	access.token.claim
14d169d3-8248-4c78-85d6-e482b7373a1d	updated_at	claim.name
14d169d3-8248-4c78-85d6-e482b7373a1d	long	jsonType.label
199f43c3-6824-404d-9270-f555c3a4677a	true	introspection.token.claim
199f43c3-6824-404d-9270-f555c3a4677a	true	userinfo.token.claim
199f43c3-6824-404d-9270-f555c3a4677a	website	user.attribute
199f43c3-6824-404d-9270-f555c3a4677a	true	id.token.claim
199f43c3-6824-404d-9270-f555c3a4677a	true	access.token.claim
199f43c3-6824-404d-9270-f555c3a4677a	website	claim.name
199f43c3-6824-404d-9270-f555c3a4677a	String	jsonType.label
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	true	introspection.token.claim
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	true	userinfo.token.claim
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	birthdate	user.attribute
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	true	id.token.claim
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	true	access.token.claim
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	birthdate	claim.name
34d92e0c-b7c7-44d8-be95-0a2d742cf1a1	String	jsonType.label
507c7984-58ff-4065-b724-6fda82df8a50	true	introspection.token.claim
507c7984-58ff-4065-b724-6fda82df8a50	true	userinfo.token.claim
507c7984-58ff-4065-b724-6fda82df8a50	gender	user.attribute
507c7984-58ff-4065-b724-6fda82df8a50	true	id.token.claim
507c7984-58ff-4065-b724-6fda82df8a50	true	access.token.claim
507c7984-58ff-4065-b724-6fda82df8a50	gender	claim.name
507c7984-58ff-4065-b724-6fda82df8a50	String	jsonType.label
77a7538a-fc79-4214-b2f8-c3fe95363ceb	true	introspection.token.claim
77a7538a-fc79-4214-b2f8-c3fe95363ceb	true	userinfo.token.claim
77a7538a-fc79-4214-b2f8-c3fe95363ceb	firstName	user.attribute
77a7538a-fc79-4214-b2f8-c3fe95363ceb	true	id.token.claim
77a7538a-fc79-4214-b2f8-c3fe95363ceb	true	access.token.claim
77a7538a-fc79-4214-b2f8-c3fe95363ceb	given_name	claim.name
77a7538a-fc79-4214-b2f8-c3fe95363ceb	String	jsonType.label
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	true	introspection.token.claim
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	true	userinfo.token.claim
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	picture	user.attribute
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	true	id.token.claim
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	true	access.token.claim
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	picture	claim.name
9ebef2c1-a670-4ed2-9d9a-dd1733b741a9	String	jsonType.label
b393d3f1-525d-4cd5-b509-966538547667	true	introspection.token.claim
b393d3f1-525d-4cd5-b509-966538547667	true	userinfo.token.claim
b393d3f1-525d-4cd5-b509-966538547667	true	id.token.claim
b393d3f1-525d-4cd5-b509-966538547667	true	access.token.claim
b7e8eec6-483b-4321-9844-f11fc09ed7d4	true	introspection.token.claim
b7e8eec6-483b-4321-9844-f11fc09ed7d4	true	userinfo.token.claim
b7e8eec6-483b-4321-9844-f11fc09ed7d4	middleName	user.attribute
b7e8eec6-483b-4321-9844-f11fc09ed7d4	true	id.token.claim
b7e8eec6-483b-4321-9844-f11fc09ed7d4	true	access.token.claim
b7e8eec6-483b-4321-9844-f11fc09ed7d4	middle_name	claim.name
b7e8eec6-483b-4321-9844-f11fc09ed7d4	String	jsonType.label
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	true	introspection.token.claim
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	true	userinfo.token.claim
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	username	user.attribute
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	true	id.token.claim
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	true	access.token.claim
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	preferred_username	claim.name
c798aa7b-d004-4bff-b61d-b4e5b6ae9e83	String	jsonType.label
d0849a4e-c639-4346-be34-03ef2628ff60	true	introspection.token.claim
d0849a4e-c639-4346-be34-03ef2628ff60	true	userinfo.token.claim
d0849a4e-c639-4346-be34-03ef2628ff60	nickname	user.attribute
d0849a4e-c639-4346-be34-03ef2628ff60	true	id.token.claim
d0849a4e-c639-4346-be34-03ef2628ff60	true	access.token.claim
d0849a4e-c639-4346-be34-03ef2628ff60	nickname	claim.name
d0849a4e-c639-4346-be34-03ef2628ff60	String	jsonType.label
f47b4172-1953-44a7-83a7-7415e74bd594	true	introspection.token.claim
f47b4172-1953-44a7-83a7-7415e74bd594	true	userinfo.token.claim
f47b4172-1953-44a7-83a7-7415e74bd594	lastName	user.attribute
f47b4172-1953-44a7-83a7-7415e74bd594	true	id.token.claim
f47b4172-1953-44a7-83a7-7415e74bd594	true	access.token.claim
f47b4172-1953-44a7-83a7-7415e74bd594	family_name	claim.name
f47b4172-1953-44a7-83a7-7415e74bd594	String	jsonType.label
fe0545e6-98f9-48dd-ad25-bde381fcb03c	true	introspection.token.claim
fe0545e6-98f9-48dd-ad25-bde381fcb03c	true	userinfo.token.claim
fe0545e6-98f9-48dd-ad25-bde381fcb03c	locale	user.attribute
fe0545e6-98f9-48dd-ad25-bde381fcb03c	true	id.token.claim
fe0545e6-98f9-48dd-ad25-bde381fcb03c	true	access.token.claim
fe0545e6-98f9-48dd-ad25-bde381fcb03c	locale	claim.name
fe0545e6-98f9-48dd-ad25-bde381fcb03c	String	jsonType.label
06f5ad90-70f7-47c3-8020-526fa4f67321	true	introspection.token.claim
06f5ad90-70f7-47c3-8020-526fa4f67321	true	userinfo.token.claim
06f5ad90-70f7-47c3-8020-526fa4f67321	email	user.attribute
06f5ad90-70f7-47c3-8020-526fa4f67321	true	id.token.claim
06f5ad90-70f7-47c3-8020-526fa4f67321	true	access.token.claim
06f5ad90-70f7-47c3-8020-526fa4f67321	email	claim.name
06f5ad90-70f7-47c3-8020-526fa4f67321	String	jsonType.label
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	true	introspection.token.claim
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	true	userinfo.token.claim
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	emailVerified	user.attribute
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	true	id.token.claim
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	true	access.token.claim
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	email_verified	claim.name
c9cf4a5a-8bc5-4954-83cf-ce43e4cc9854	boolean	jsonType.label
5ba88915-aa83-457d-8da5-b5be006c4b09	formatted	user.attribute.formatted
5ba88915-aa83-457d-8da5-b5be006c4b09	country	user.attribute.country
5ba88915-aa83-457d-8da5-b5be006c4b09	true	introspection.token.claim
5ba88915-aa83-457d-8da5-b5be006c4b09	postal_code	user.attribute.postal_code
5ba88915-aa83-457d-8da5-b5be006c4b09	true	userinfo.token.claim
5ba88915-aa83-457d-8da5-b5be006c4b09	street	user.attribute.street
5ba88915-aa83-457d-8da5-b5be006c4b09	true	id.token.claim
5ba88915-aa83-457d-8da5-b5be006c4b09	region	user.attribute.region
5ba88915-aa83-457d-8da5-b5be006c4b09	true	access.token.claim
5ba88915-aa83-457d-8da5-b5be006c4b09	locality	user.attribute.locality
15f64c34-bdfd-40fe-92e4-67d73056ee80	true	introspection.token.claim
15f64c34-bdfd-40fe-92e4-67d73056ee80	true	userinfo.token.claim
15f64c34-bdfd-40fe-92e4-67d73056ee80	phoneNumber	user.attribute
15f64c34-bdfd-40fe-92e4-67d73056ee80	true	id.token.claim
15f64c34-bdfd-40fe-92e4-67d73056ee80	true	access.token.claim
15f64c34-bdfd-40fe-92e4-67d73056ee80	phone_number	claim.name
15f64c34-bdfd-40fe-92e4-67d73056ee80	String	jsonType.label
a819e220-7d82-4d58-8ef5-a837fb318239	true	introspection.token.claim
a819e220-7d82-4d58-8ef5-a837fb318239	true	userinfo.token.claim
a819e220-7d82-4d58-8ef5-a837fb318239	phoneNumberVerified	user.attribute
a819e220-7d82-4d58-8ef5-a837fb318239	true	id.token.claim
a819e220-7d82-4d58-8ef5-a837fb318239	true	access.token.claim
a819e220-7d82-4d58-8ef5-a837fb318239	phone_number_verified	claim.name
a819e220-7d82-4d58-8ef5-a837fb318239	boolean	jsonType.label
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	true	introspection.token.claim
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	true	multivalued
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	foo	user.attribute
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	true	access.token.claim
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	resource_access.${client_id}.roles	claim.name
c3c87ee2-523c-42fd-a3c5-49ec1bcc3a35	String	jsonType.label
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	true	introspection.token.claim
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	true	multivalued
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	foo	user.attribute
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	true	access.token.claim
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	realm_access.roles	claim.name
da32cc1f-bcf6-4fe2-b7d3-90fcab4544b1	String	jsonType.label
e6d7361d-d8d0-406c-a481-5a4ebf8ea2c6	true	introspection.token.claim
e6d7361d-d8d0-406c-a481-5a4ebf8ea2c6	true	access.token.claim
d4b1c12c-db26-46ee-9683-d2fd476aaa69	true	introspection.token.claim
d4b1c12c-db26-46ee-9683-d2fd476aaa69	true	access.token.claim
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	true	introspection.token.claim
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	true	userinfo.token.claim
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	username	user.attribute
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	true	id.token.claim
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	true	access.token.claim
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	upn	claim.name
d6ce1f1a-2174-4834-b79f-ed24ca58cb4d	String	jsonType.label
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	true	introspection.token.claim
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	true	multivalued
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	foo	user.attribute
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	true	id.token.claim
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	true	access.token.claim
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	groups	claim.name
e00ef2c8-fa01-418e-b8f6-36f0e9d9b7cb	String	jsonType.label
508693ad-b1b7-40fd-ad54-20ec2fa369c1	true	introspection.token.claim
508693ad-b1b7-40fd-ad54-20ec2fa369c1	true	id.token.claim
508693ad-b1b7-40fd-ad54-20ec2fa369c1	true	access.token.claim
14900a52-4f03-48f3-a68c-4eb6715c8196	true	introspection.token.claim
14900a52-4f03-48f3-a68c-4eb6715c8196	true	access.token.claim
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	AUTH_TIME	user.session.note
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	true	introspection.token.claim
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	true	id.token.claim
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	true	access.token.claim
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	auth_time	claim.name
92d6f292-425d-41e7-b032-3dbc6bcd5c1c	long	jsonType.label
68575c42-31c9-4dd0-a2a3-ebcfde131db6	false	single
68575c42-31c9-4dd0-a2a3-ebcfde131db6	Basic	attribute.nameformat
68575c42-31c9-4dd0-a2a3-ebcfde131db6	Role	attribute.name
10ca056c-cef6-4535-ab57-1201c7db2f8a	true	introspection.token.claim
10ca056c-cef6-4535-ab57-1201c7db2f8a	true	userinfo.token.claim
10ca056c-cef6-4535-ab57-1201c7db2f8a	lastName	user.attribute
10ca056c-cef6-4535-ab57-1201c7db2f8a	true	id.token.claim
10ca056c-cef6-4535-ab57-1201c7db2f8a	true	access.token.claim
10ca056c-cef6-4535-ab57-1201c7db2f8a	family_name	claim.name
10ca056c-cef6-4535-ab57-1201c7db2f8a	String	jsonType.label
21f1e2f7-d02a-4602-9f63-135d8decf653	true	introspection.token.claim
21f1e2f7-d02a-4602-9f63-135d8decf653	true	userinfo.token.claim
21f1e2f7-d02a-4602-9f63-135d8decf653	true	id.token.claim
21f1e2f7-d02a-4602-9f63-135d8decf653	true	access.token.claim
23fc83d5-32ef-40e1-b240-ec5d6101f37c	true	introspection.token.claim
23fc83d5-32ef-40e1-b240-ec5d6101f37c	true	userinfo.token.claim
23fc83d5-32ef-40e1-b240-ec5d6101f37c	username	user.attribute
23fc83d5-32ef-40e1-b240-ec5d6101f37c	true	id.token.claim
23fc83d5-32ef-40e1-b240-ec5d6101f37c	true	access.token.claim
23fc83d5-32ef-40e1-b240-ec5d6101f37c	preferred_username	claim.name
23fc83d5-32ef-40e1-b240-ec5d6101f37c	String	jsonType.label
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	true	introspection.token.claim
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	true	userinfo.token.claim
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	birthdate	user.attribute
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	true	id.token.claim
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	true	access.token.claim
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	birthdate	claim.name
2c15fcca-7064-4e6e-8f47-5d946abc1fbe	String	jsonType.label
399839c9-4d48-419f-a6d1-692b74120ce7	true	introspection.token.claim
399839c9-4d48-419f-a6d1-692b74120ce7	true	userinfo.token.claim
399839c9-4d48-419f-a6d1-692b74120ce7	firstName	user.attribute
399839c9-4d48-419f-a6d1-692b74120ce7	true	id.token.claim
399839c9-4d48-419f-a6d1-692b74120ce7	true	access.token.claim
399839c9-4d48-419f-a6d1-692b74120ce7	given_name	claim.name
399839c9-4d48-419f-a6d1-692b74120ce7	String	jsonType.label
48b57352-be17-4053-8156-97e13a1127df	true	introspection.token.claim
48b57352-be17-4053-8156-97e13a1127df	true	userinfo.token.claim
48b57352-be17-4053-8156-97e13a1127df	updatedAt	user.attribute
48b57352-be17-4053-8156-97e13a1127df	true	id.token.claim
48b57352-be17-4053-8156-97e13a1127df	true	access.token.claim
48b57352-be17-4053-8156-97e13a1127df	updated_at	claim.name
48b57352-be17-4053-8156-97e13a1127df	long	jsonType.label
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	true	introspection.token.claim
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	true	userinfo.token.claim
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	zoneinfo	user.attribute
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	true	id.token.claim
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	true	access.token.claim
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	zoneinfo	claim.name
7ab8eed3-1750-4243-a464-e9a2fa95fd8e	String	jsonType.label
86c4958c-ee18-4b65-917c-0632759d87b4	true	introspection.token.claim
86c4958c-ee18-4b65-917c-0632759d87b4	true	userinfo.token.claim
86c4958c-ee18-4b65-917c-0632759d87b4	website	user.attribute
86c4958c-ee18-4b65-917c-0632759d87b4	true	id.token.claim
86c4958c-ee18-4b65-917c-0632759d87b4	true	access.token.claim
86c4958c-ee18-4b65-917c-0632759d87b4	website	claim.name
86c4958c-ee18-4b65-917c-0632759d87b4	String	jsonType.label
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	true	introspection.token.claim
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	true	userinfo.token.claim
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	nickname	user.attribute
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	true	id.token.claim
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	true	access.token.claim
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	nickname	claim.name
8d4bbdc6-99fa-4ddd-81a4-f342f31e816f	String	jsonType.label
a304d0a2-bdcb-4307-a485-bb21c17a68f2	true	introspection.token.claim
a304d0a2-bdcb-4307-a485-bb21c17a68f2	true	userinfo.token.claim
a304d0a2-bdcb-4307-a485-bb21c17a68f2	picture	user.attribute
a304d0a2-bdcb-4307-a485-bb21c17a68f2	true	id.token.claim
a304d0a2-bdcb-4307-a485-bb21c17a68f2	true	access.token.claim
a304d0a2-bdcb-4307-a485-bb21c17a68f2	picture	claim.name
a304d0a2-bdcb-4307-a485-bb21c17a68f2	String	jsonType.label
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	true	introspection.token.claim
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	true	userinfo.token.claim
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	gender	user.attribute
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	true	id.token.claim
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	true	access.token.claim
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	gender	claim.name
a642eb71-7412-4ae8-b6fb-f8d60a03de1c	String	jsonType.label
ab7f1e8a-add2-4ce1-a398-41465669f0c2	true	introspection.token.claim
ab7f1e8a-add2-4ce1-a398-41465669f0c2	true	userinfo.token.claim
ab7f1e8a-add2-4ce1-a398-41465669f0c2	locale	user.attribute
ab7f1e8a-add2-4ce1-a398-41465669f0c2	true	id.token.claim
ab7f1e8a-add2-4ce1-a398-41465669f0c2	true	access.token.claim
ab7f1e8a-add2-4ce1-a398-41465669f0c2	locale	claim.name
ab7f1e8a-add2-4ce1-a398-41465669f0c2	String	jsonType.label
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	true	introspection.token.claim
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	true	userinfo.token.claim
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	profile	user.attribute
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	true	id.token.claim
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	true	access.token.claim
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	profile	claim.name
ac75fd8e-ee6b-43e2-86bd-bad56f55f763	String	jsonType.label
c4def597-fca6-47bc-a5da-a47990da02da	true	introspection.token.claim
c4def597-fca6-47bc-a5da-a47990da02da	true	userinfo.token.claim
c4def597-fca6-47bc-a5da-a47990da02da	middleName	user.attribute
c4def597-fca6-47bc-a5da-a47990da02da	true	id.token.claim
c4def597-fca6-47bc-a5da-a47990da02da	true	access.token.claim
c4def597-fca6-47bc-a5da-a47990da02da	middle_name	claim.name
c4def597-fca6-47bc-a5da-a47990da02da	String	jsonType.label
014e1483-9907-4925-a967-ad8db6194b18	true	introspection.token.claim
014e1483-9907-4925-a967-ad8db6194b18	true	userinfo.token.claim
014e1483-9907-4925-a967-ad8db6194b18	emailVerified	user.attribute
014e1483-9907-4925-a967-ad8db6194b18	true	id.token.claim
014e1483-9907-4925-a967-ad8db6194b18	true	access.token.claim
014e1483-9907-4925-a967-ad8db6194b18	email_verified	claim.name
014e1483-9907-4925-a967-ad8db6194b18	boolean	jsonType.label
44f9792e-6948-4c5f-bc7a-6b79396de006	true	introspection.token.claim
44f9792e-6948-4c5f-bc7a-6b79396de006	true	userinfo.token.claim
44f9792e-6948-4c5f-bc7a-6b79396de006	email	user.attribute
44f9792e-6948-4c5f-bc7a-6b79396de006	true	id.token.claim
44f9792e-6948-4c5f-bc7a-6b79396de006	true	access.token.claim
44f9792e-6948-4c5f-bc7a-6b79396de006	email	claim.name
44f9792e-6948-4c5f-bc7a-6b79396de006	String	jsonType.label
baf54769-b86d-46ae-abb8-e9be7e344881	formatted	user.attribute.formatted
baf54769-b86d-46ae-abb8-e9be7e344881	country	user.attribute.country
baf54769-b86d-46ae-abb8-e9be7e344881	true	introspection.token.claim
baf54769-b86d-46ae-abb8-e9be7e344881	postal_code	user.attribute.postal_code
baf54769-b86d-46ae-abb8-e9be7e344881	true	userinfo.token.claim
baf54769-b86d-46ae-abb8-e9be7e344881	street	user.attribute.street
baf54769-b86d-46ae-abb8-e9be7e344881	true	id.token.claim
baf54769-b86d-46ae-abb8-e9be7e344881	region	user.attribute.region
baf54769-b86d-46ae-abb8-e9be7e344881	true	access.token.claim
baf54769-b86d-46ae-abb8-e9be7e344881	locality	user.attribute.locality
337427b0-248a-4d62-8b4a-71c705e03a06	true	introspection.token.claim
337427b0-248a-4d62-8b4a-71c705e03a06	true	userinfo.token.claim
337427b0-248a-4d62-8b4a-71c705e03a06	phoneNumber	user.attribute
337427b0-248a-4d62-8b4a-71c705e03a06	true	id.token.claim
337427b0-248a-4d62-8b4a-71c705e03a06	true	access.token.claim
337427b0-248a-4d62-8b4a-71c705e03a06	phone_number	claim.name
337427b0-248a-4d62-8b4a-71c705e03a06	String	jsonType.label
d567fc4c-5db9-49e4-b36e-bf092953cd75	true	introspection.token.claim
d567fc4c-5db9-49e4-b36e-bf092953cd75	true	userinfo.token.claim
d567fc4c-5db9-49e4-b36e-bf092953cd75	phoneNumberVerified	user.attribute
d567fc4c-5db9-49e4-b36e-bf092953cd75	true	id.token.claim
d567fc4c-5db9-49e4-b36e-bf092953cd75	true	access.token.claim
d567fc4c-5db9-49e4-b36e-bf092953cd75	phone_number_verified	claim.name
d567fc4c-5db9-49e4-b36e-bf092953cd75	boolean	jsonType.label
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	true	introspection.token.claim
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	true	multivalued
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	foo	user.attribute
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	true	access.token.claim
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	resource_access.${client_id}.roles	claim.name
00d52a3f-ff81-406d-8cb7-ccbc2d660f95	String	jsonType.label
35ca1a32-edd5-40cc-af4a-0565e6797abc	true	introspection.token.claim
35ca1a32-edd5-40cc-af4a-0565e6797abc	true	multivalued
35ca1a32-edd5-40cc-af4a-0565e6797abc	foo	user.attribute
35ca1a32-edd5-40cc-af4a-0565e6797abc	true	access.token.claim
35ca1a32-edd5-40cc-af4a-0565e6797abc	realm_access.roles	claim.name
35ca1a32-edd5-40cc-af4a-0565e6797abc	String	jsonType.label
7362e0d7-227e-4944-8ff9-39a8bfeef0e4	true	introspection.token.claim
7362e0d7-227e-4944-8ff9-39a8bfeef0e4	true	access.token.claim
c96b3fc3-a9b5-44d4-8bb9-70f41adcce89	true	introspection.token.claim
c96b3fc3-a9b5-44d4-8bb9-70f41adcce89	true	access.token.claim
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	true	introspection.token.claim
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	true	multivalued
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	foo	user.attribute
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	true	id.token.claim
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	true	access.token.claim
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	groups	claim.name
508f3b8d-492f-4bfa-bacb-a7a9363ca6db	String	jsonType.label
afbf0361-f65a-43ed-a1e0-430b7f3288e7	true	introspection.token.claim
afbf0361-f65a-43ed-a1e0-430b7f3288e7	true	userinfo.token.claim
afbf0361-f65a-43ed-a1e0-430b7f3288e7	username	user.attribute
afbf0361-f65a-43ed-a1e0-430b7f3288e7	true	id.token.claim
afbf0361-f65a-43ed-a1e0-430b7f3288e7	true	access.token.claim
afbf0361-f65a-43ed-a1e0-430b7f3288e7	upn	claim.name
afbf0361-f65a-43ed-a1e0-430b7f3288e7	String	jsonType.label
808283b3-4553-4413-9dd5-d97ddb9cfb57	true	introspection.token.claim
808283b3-4553-4413-9dd5-d97ddb9cfb57	true	id.token.claim
808283b3-4553-4413-9dd5-d97ddb9cfb57	true	access.token.claim
a15e9e6f-c939-4818-b1c5-315139640583	AUTH_TIME	user.session.note
a15e9e6f-c939-4818-b1c5-315139640583	true	introspection.token.claim
a15e9e6f-c939-4818-b1c5-315139640583	true	id.token.claim
a15e9e6f-c939-4818-b1c5-315139640583	true	access.token.claim
a15e9e6f-c939-4818-b1c5-315139640583	auth_time	claim.name
a15e9e6f-c939-4818-b1c5-315139640583	long	jsonType.label
adc4fd89-a051-4265-bf9f-7964703140c5	true	introspection.token.claim
adc4fd89-a051-4265-bf9f-7964703140c5	true	access.token.claim
0364520e-6da8-4bec-ac91-73266daa1e71	clientAddress	user.session.note
0364520e-6da8-4bec-ac91-73266daa1e71	true	introspection.token.claim
0364520e-6da8-4bec-ac91-73266daa1e71	true	id.token.claim
0364520e-6da8-4bec-ac91-73266daa1e71	true	access.token.claim
0364520e-6da8-4bec-ac91-73266daa1e71	clientAddress	claim.name
0364520e-6da8-4bec-ac91-73266daa1e71	String	jsonType.label
18f602f7-005d-4424-a5b5-4018fb921645	clientHost	user.session.note
18f602f7-005d-4424-a5b5-4018fb921645	true	introspection.token.claim
18f602f7-005d-4424-a5b5-4018fb921645	true	id.token.claim
18f602f7-005d-4424-a5b5-4018fb921645	true	access.token.claim
18f602f7-005d-4424-a5b5-4018fb921645	clientHost	claim.name
18f602f7-005d-4424-a5b5-4018fb921645	String	jsonType.label
73b580aa-54ba-4c4a-9b84-5663fd326daa	client_id	user.session.note
73b580aa-54ba-4c4a-9b84-5663fd326daa	true	introspection.token.claim
73b580aa-54ba-4c4a-9b84-5663fd326daa	true	id.token.claim
73b580aa-54ba-4c4a-9b84-5663fd326daa	true	access.token.claim
73b580aa-54ba-4c4a-9b84-5663fd326daa	client_id	claim.name
73b580aa-54ba-4c4a-9b84-5663fd326daa	String	jsonType.label
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	true	introspection.token.claim
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	true	userinfo.token.claim
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	locale	user.attribute
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	true	id.token.claim
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	true	access.token.claim
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	locale	claim.name
b9b9d7d0-16aa-45c0-95a1-5104f2a8c135	String	jsonType.label
\.


--
-- Data for Name: realm; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm (id, access_code_lifespan, user_action_lifespan, access_token_lifespan, account_theme, admin_theme, email_theme, enabled, events_enabled, events_expiration, login_theme, name, not_before, password_policy, registration_allowed, remember_me, reset_password_allowed, social, ssl_required, sso_idle_timeout, sso_max_lifespan, update_profile_on_soc_login, verify_email, master_admin_client, login_lifespan, internationalization_enabled, default_locale, reg_email_as_username, admin_events_enabled, admin_events_details_enabled, edit_username_allowed, otp_policy_counter, otp_policy_window, otp_policy_period, otp_policy_digits, otp_policy_alg, otp_policy_type, browser_flow, registration_flow, direct_grant_flow, reset_credentials_flow, client_auth_flow, offline_session_idle_timeout, revoke_refresh_token, access_token_life_implicit, login_with_email_allowed, duplicate_emails_allowed, docker_auth_flow, refresh_token_max_reuse, allow_user_managed_access, sso_max_lifespan_remember_me, sso_idle_timeout_remember_me, default_role) FROM stdin;
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	60	300	60	\N	\N	\N	t	f	0	\N	master	0	\N	f	f	f	f	EXTERNAL	1800	36000	f	f	25a276e3-07eb-49e9-86a9-5a15a5f09800	1800	f	\N	f	f	f	f	0	1	30	6	HmacSHA1	totp	999b03f6-bc36-4d0d-86c6-f5770b4491e0	a836592f-06cc-4a7d-81c8-ca9cbefe27a4	f6e06a1b-3eb4-4715-9d69-d39b0b661faa	3d65f07f-1929-4bc5-9f25-fd2dfe675142	4ee9f7ca-86ad-4489-b866-392c6c62caa1	2592000	f	900	t	f	4c7e065b-0f1d-41d7-845c-3afed6616336	0	f	0	0	c5f92874-1f2c-42cf-ad4f-a4ccf962cce9
6a264182-ab2b-4da7-a868-c7dddf4329f2	60	300	300	\N	\N	\N	t	f	0	\N	pulse	0	length(12) and upperCase(1) and lowerCase(1) and digits(1) and specialChars(1) and notUsername(undefined)	f	f	t	f	EXTERNAL	1800	36000	f	f	724428c1-ccb1-4367-87f8-64d2d37295e8	1800	f	\N	f	f	f	f	0	1	30	6	HmacSHA1	totp	a2587804-176c-450d-9be8-0744f47249ab	92d62f3e-ada7-4f9e-9454-a9921fa2918c	6e9428d2-d658-43f7-97c6-315bf26de400	640f6c14-8515-407e-8928-4729fa870ea4	d799aeff-0c88-416b-a0b7-c405d98330a1	2592000	f	900	t	f	a7cd6873-6e89-4138-bb20-2e6fdf8c3b40	0	f	0	0	c2043b06-2175-4019-89aa-9bef1b881b62
\.


--
-- Data for Name: realm_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_attribute (name, realm_id, value) FROM stdin;
_browser_header.contentSecurityPolicyReportOnly	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	
_browser_header.xContentTypeOptions	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	nosniff
_browser_header.referrerPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	no-referrer
_browser_header.xRobotsTag	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	none
_browser_header.xFrameOptions	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	SAMEORIGIN
_browser_header.contentSecurityPolicy	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	frame-src 'self'; frame-ancestors 'self'; object-src 'none';
_browser_header.xXSSProtection	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	1; mode=block
_browser_header.strictTransportSecurity	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	max-age=31536000; includeSubDomains
bruteForceProtected	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	false
permanentLockout	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	false
maxTemporaryLockouts	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	0
maxFailureWaitSeconds	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	900
minimumQuickLoginWaitSeconds	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	60
waitIncrementSeconds	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	60
quickLoginCheckMilliSeconds	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	1000
maxDeltaTimeSeconds	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	43200
failureFactor	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	30
realmReusableOtpCode	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	false
firstBrokerLoginFlowId	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	988f94e6-631a-4993-ad60-528952242c61
displayName	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	Keycloak
displayNameHtml	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	<div class="kc-logo-text"><span>Keycloak</span></div>
defaultSignatureAlgorithm	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	RS256
offlineSessionMaxLifespanEnabled	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	false
offlineSessionMaxLifespan	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	5184000
_browser_header.contentSecurityPolicyReportOnly	6a264182-ab2b-4da7-a868-c7dddf4329f2	
_browser_header.xContentTypeOptions	6a264182-ab2b-4da7-a868-c7dddf4329f2	nosniff
_browser_header.referrerPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	no-referrer
_browser_header.xRobotsTag	6a264182-ab2b-4da7-a868-c7dddf4329f2	none
_browser_header.xFrameOptions	6a264182-ab2b-4da7-a868-c7dddf4329f2	SAMEORIGIN
_browser_header.contentSecurityPolicy	6a264182-ab2b-4da7-a868-c7dddf4329f2	frame-src 'self'; frame-ancestors 'self'; object-src 'none';
_browser_header.xXSSProtection	6a264182-ab2b-4da7-a868-c7dddf4329f2	1; mode=block
_browser_header.strictTransportSecurity	6a264182-ab2b-4da7-a868-c7dddf4329f2	max-age=31536000; includeSubDomains
permanentLockout	6a264182-ab2b-4da7-a868-c7dddf4329f2	false
maxTemporaryLockouts	6a264182-ab2b-4da7-a868-c7dddf4329f2	0
maxFailureWaitSeconds	6a264182-ab2b-4da7-a868-c7dddf4329f2	900
minimumQuickLoginWaitSeconds	6a264182-ab2b-4da7-a868-c7dddf4329f2	60
waitIncrementSeconds	6a264182-ab2b-4da7-a868-c7dddf4329f2	60
quickLoginCheckMilliSeconds	6a264182-ab2b-4da7-a868-c7dddf4329f2	1000
maxDeltaTimeSeconds	6a264182-ab2b-4da7-a868-c7dddf4329f2	43200
realmReusableOtpCode	6a264182-ab2b-4da7-a868-c7dddf4329f2	false
displayName	6a264182-ab2b-4da7-a868-c7dddf4329f2	Pulse RH
displayNameHtml	6a264182-ab2b-4da7-a868-c7dddf4329f2	<b>Pulse RH</b>
defaultSignatureAlgorithm	6a264182-ab2b-4da7-a868-c7dddf4329f2	RS256
bruteForceProtected	6a264182-ab2b-4da7-a868-c7dddf4329f2	true
failureFactor	6a264182-ab2b-4da7-a868-c7dddf4329f2	5
offlineSessionMaxLifespanEnabled	6a264182-ab2b-4da7-a868-c7dddf4329f2	false
offlineSessionMaxLifespan	6a264182-ab2b-4da7-a868-c7dddf4329f2	5184000
actionTokenGeneratedByAdminLifespan	6a264182-ab2b-4da7-a868-c7dddf4329f2	43200
actionTokenGeneratedByUserLifespan	6a264182-ab2b-4da7-a868-c7dddf4329f2	300
oauth2DeviceCodeLifespan	6a264182-ab2b-4da7-a868-c7dddf4329f2	600
oauth2DevicePollingInterval	6a264182-ab2b-4da7-a868-c7dddf4329f2	5
webAuthnPolicyRpEntityName	6a264182-ab2b-4da7-a868-c7dddf4329f2	keycloak
webAuthnPolicySignatureAlgorithms	6a264182-ab2b-4da7-a868-c7dddf4329f2	ES256
webAuthnPolicyRpId	6a264182-ab2b-4da7-a868-c7dddf4329f2	
webAuthnPolicyAttestationConveyancePreference	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyAuthenticatorAttachment	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyRequireResidentKey	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyUserVerificationRequirement	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyCreateTimeout	6a264182-ab2b-4da7-a868-c7dddf4329f2	0
webAuthnPolicyAvoidSameAuthenticatorRegister	6a264182-ab2b-4da7-a868-c7dddf4329f2	false
webAuthnPolicyRpEntityNamePasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	keycloak
webAuthnPolicySignatureAlgorithmsPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	ES256
webAuthnPolicyRpIdPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	
webAuthnPolicyAttestationConveyancePreferencePasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyAuthenticatorAttachmentPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyRequireResidentKeyPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyUserVerificationRequirementPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	not specified
webAuthnPolicyCreateTimeoutPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	0
webAuthnPolicyAvoidSameAuthenticatorRegisterPasswordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	false
cibaBackchannelTokenDeliveryMode	6a264182-ab2b-4da7-a868-c7dddf4329f2	poll
cibaExpiresIn	6a264182-ab2b-4da7-a868-c7dddf4329f2	120
cibaInterval	6a264182-ab2b-4da7-a868-c7dddf4329f2	5
cibaAuthRequestedUserHint	6a264182-ab2b-4da7-a868-c7dddf4329f2	login_hint
parRequestUriLifespan	6a264182-ab2b-4da7-a868-c7dddf4329f2	60
firstBrokerLoginFlowId	6a264182-ab2b-4da7-a868-c7dddf4329f2	38bbbaea-251b-4915-978f-90c3fb1a26cb
\.


--
-- Data for Name: realm_default_groups; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_default_groups (realm_id, group_id) FROM stdin;
\.


--
-- Data for Name: realm_enabled_event_types; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_enabled_event_types (realm_id, value) FROM stdin;
\.


--
-- Data for Name: realm_events_listeners; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_events_listeners (realm_id, value) FROM stdin;
1aecbfb5-44bb-49c8-a2ef-ef77293e300d	jboss-logging
6a264182-ab2b-4da7-a868-c7dddf4329f2	jboss-logging
\.


--
-- Data for Name: realm_localizations; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_localizations (realm_id, locale, texts) FROM stdin;
\.


--
-- Data for Name: realm_required_credential; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_required_credential (type, form_label, input, secret, realm_id) FROM stdin;
password	password	t	t	1aecbfb5-44bb-49c8-a2ef-ef77293e300d
password	password	t	t	6a264182-ab2b-4da7-a868-c7dddf4329f2
\.


--
-- Data for Name: realm_smtp_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_smtp_config (realm_id, value, name) FROM stdin;
\.


--
-- Data for Name: realm_supported_locales; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.realm_supported_locales (realm_id, value) FROM stdin;
\.


--
-- Data for Name: redirect_uris; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.redirect_uris (client_id, value) FROM stdin;
28a13f19-a581-48cf-9d27-203c80b5be3a	/realms/master/account/*
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	/realms/master/account/*
c9127146-5188-4383-bc83-8371c445ed88	/admin/master/console/*
6d6f00fd-79c0-4acc-a3de-b28063ec0926	/realms/pulse/account/*
d2e77719-c7fa-48e1-9d93-95b5f409862a	/realms/pulse/account/*
94b40267-f844-4f8e-996e-3bc5b0800c08	/admin/pulse/console/*
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	https://app.pulse.local/*
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	http://localhost:3000/*
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	https://prometheus.pulse.local/*
\.


--
-- Data for Name: required_action_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.required_action_config (required_action_id, value, name) FROM stdin;
\.


--
-- Data for Name: required_action_provider; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.required_action_provider (id, alias, name, realm_id, enabled, default_action, provider_id, priority) FROM stdin;
09194c60-aff8-4388-96eb-e13cb84f76b3	VERIFY_EMAIL	Verify Email	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	VERIFY_EMAIL	50
dab2e809-8e1d-4f1c-9f02-b5c513c5a3e5	UPDATE_PROFILE	Update Profile	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	UPDATE_PROFILE	40
14bf714f-1823-43d8-b23c-24133ed7f52d	CONFIGURE_TOTP	Configure OTP	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	CONFIGURE_TOTP	10
8c780d76-a79b-4850-921a-284d30221a17	UPDATE_PASSWORD	Update Password	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	UPDATE_PASSWORD	30
024bc9f2-e1ad-4b5e-85c4-bdaea69cc6d3	TERMS_AND_CONDITIONS	Terms and Conditions	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	f	TERMS_AND_CONDITIONS	20
1f53c6c3-fa43-4d41-b125-c2b3618a0c85	delete_account	Delete Account	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	f	f	delete_account	60
cdf2c2a9-4538-4e0d-bc6d-992615d09d2b	delete_credential	Delete Credential	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	delete_credential	100
92deb4a8-6201-4d3e-9a2d-f40dac980f30	update_user_locale	Update User Locale	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	update_user_locale	1000
c8502880-a70f-42bc-83e9-92fd3c68eee5	webauthn-register	Webauthn Register	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	webauthn-register	70
729bc2a6-0807-4596-a93e-2305761b2e68	webauthn-register-passwordless	Webauthn Register Passwordless	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	webauthn-register-passwordless	80
3573c5a5-5502-4156-b3cd-e1349da9f2d0	VERIFY_PROFILE	Verify Profile	1aecbfb5-44bb-49c8-a2ef-ef77293e300d	t	f	VERIFY_PROFILE	90
406ffa6a-b070-4a4a-be6d-3040b14288d8	VERIFY_EMAIL	Verify Email	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	VERIFY_EMAIL	50
0d1d2478-e5d9-4ec9-a901-bff614f8463f	UPDATE_PROFILE	Update Profile	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	UPDATE_PROFILE	40
97cf38a9-d9e4-4a88-8303-0a40456f6b45	CONFIGURE_TOTP	Configure OTP	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	CONFIGURE_TOTP	10
164fefc9-09cd-4823-8e06-dcad4e012b43	UPDATE_PASSWORD	Update Password	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	UPDATE_PASSWORD	30
4acf9514-9f77-40bd-9928-912004f8e392	TERMS_AND_CONDITIONS	Terms and Conditions	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	f	TERMS_AND_CONDITIONS	20
2b648ec5-267e-4a8c-bde4-4fa2c52b199a	delete_account	Delete Account	6a264182-ab2b-4da7-a868-c7dddf4329f2	f	f	delete_account	60
c071f7f0-2aad-4f4e-920f-2d58ace8d32f	delete_credential	Delete Credential	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	delete_credential	100
e1fad998-d189-4861-b7d2-4c0af37c4d40	update_user_locale	Update User Locale	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	update_user_locale	1000
830ee10c-9276-463e-8c2d-0b14b45081f0	webauthn-register	Webauthn Register	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	webauthn-register	70
f6a3d8e5-b8e2-486c-8895-7ae96f55e0b1	webauthn-register-passwordless	Webauthn Register Passwordless	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	webauthn-register-passwordless	80
4e5a4bb3-0461-4249-908d-617026a7dee8	VERIFY_PROFILE	Verify Profile	6a264182-ab2b-4da7-a868-c7dddf4329f2	t	f	VERIFY_PROFILE	90
\.


--
-- Data for Name: resource_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_attribute (id, name, value, resource_id) FROM stdin;
\.


--
-- Data for Name: resource_policy; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_policy (resource_id, policy_id) FROM stdin;
\.


--
-- Data for Name: resource_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_scope (resource_id, scope_id) FROM stdin;
\.


--
-- Data for Name: resource_server; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_server (id, allow_rs_remote_mgmt, policy_enforce_mode, decision_strategy) FROM stdin;
\.


--
-- Data for Name: resource_server_perm_ticket; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_server_perm_ticket (id, owner, requester, created_timestamp, granted_timestamp, resource_id, scope_id, resource_server_id, policy_id) FROM stdin;
\.


--
-- Data for Name: resource_server_policy; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_server_policy (id, name, description, type, decision_strategy, logic, resource_server_id, owner) FROM stdin;
\.


--
-- Data for Name: resource_server_resource; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_server_resource (id, name, type, icon_uri, owner, resource_server_id, owner_managed_access, display_name) FROM stdin;
\.


--
-- Data for Name: resource_server_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_server_scope (id, name, icon_uri, resource_server_id, display_name) FROM stdin;
\.


--
-- Data for Name: resource_uris; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.resource_uris (resource_id, value) FROM stdin;
\.


--
-- Data for Name: role_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.role_attribute (id, role_id, name, value) FROM stdin;
\.


--
-- Data for Name: scope_mapping; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.scope_mapping (client_id, role_id) FROM stdin;
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	ff571d5a-d56e-4937-a412-60049b740c33
2b1c80a7-fdd0-4b58-aac4-ab1dea8e83e7	e271e581-191e-4d66-ad3d-f5dcf02742ac
d2e77719-c7fa-48e1-9d93-95b5f409862a	a2640def-7dff-496a-af38-d7ec3b7f71f2
d2e77719-c7fa-48e1-9d93-95b5f409862a	f53862a5-f9b3-462e-ba32-cfccb6990d3a
\.


--
-- Data for Name: scope_policy; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.scope_policy (scope_id, policy_id) FROM stdin;
\.


--
-- Data for Name: user_attribute; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_attribute (name, value, user_id, id, long_value_hash, long_value_hash_lower_case, long_value) FROM stdin;
\.


--
-- Data for Name: user_consent; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_consent (id, client_id, user_id, created_date, last_updated_date, client_storage_provider, external_client_id) FROM stdin;
\.


--
-- Data for Name: user_consent_client_scope; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_consent_client_scope (user_consent_id, scope_id) FROM stdin;
\.


--
-- Data for Name: user_entity; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_entity (id, email, email_constraint, email_verified, enabled, federation_link, first_name, last_name, realm_id, username, created_timestamp, service_account_client_link, not_before) FROM stdin;
1cfb390e-1105-4411-8fbd-957261650f42	\N	179c1042-6a76-4d31-9ca6-052662224eb0	f	t	\N	\N	\N	6a264182-ab2b-4da7-a868-c7dddf4329f2	service-account-pulse-backend	1781028407405	710ee357-9495-4b0b-8f44-907835d002b3	0
\.


--
-- Data for Name: user_federation_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_federation_config (user_federation_provider_id, value, name) FROM stdin;
\.


--
-- Data for Name: user_federation_mapper; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_federation_mapper (id, name, federation_provider_id, federation_mapper_type, realm_id) FROM stdin;
\.


--
-- Data for Name: user_federation_mapper_config; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_federation_mapper_config (user_federation_mapper_id, value, name) FROM stdin;
\.


--
-- Data for Name: user_federation_provider; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_federation_provider (id, changed_sync_period, display_name, full_sync_period, last_sync, priority, provider_name, realm_id) FROM stdin;
\.


--
-- Data for Name: user_group_membership; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_group_membership (group_id, user_id) FROM stdin;
\.


--
-- Data for Name: user_required_action; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_required_action (user_id, required_action) FROM stdin;
\.


--
-- Data for Name: user_role_mapping; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_role_mapping (role_id, user_id) FROM stdin;
c2043b06-2175-4019-89aa-9bef1b881b62	1cfb390e-1105-4411-8fbd-957261650f42
\.


--
-- Data for Name: user_session; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_session (id, auth_method, ip_address, last_session_refresh, login_username, realm_id, remember_me, started, user_id, user_session_state, broker_session_id, broker_user_id) FROM stdin;
\.


--
-- Data for Name: user_session_note; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.user_session_note (user_session, name, value) FROM stdin;
\.


--
-- Data for Name: username_login_failure; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.username_login_failure (realm_id, username, failed_login_not_before, last_failure, last_ip_failure, num_failures) FROM stdin;
\.


--
-- Data for Name: web_origins; Type: TABLE DATA; Schema: public; Owner: keycloak_user
--

COPY public.web_origins (client_id, value) FROM stdin;
c9127146-5188-4383-bc83-8371c445ed88	+
94b40267-f844-4f8e-996e-3bc5b0800c08	+
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	https://app.pulse.local
e0315a98-0c6e-4e0d-aa20-3f7c2218afdf	http://localhost:3000
3ab40e6e-ea88-40dd-ae9b-a0760a3feef2	https://prometheus.pulse.local
\.


--
-- Name: username_login_failure CONSTRAINT_17-2; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.username_login_failure
    ADD CONSTRAINT "CONSTRAINT_17-2" PRIMARY KEY (realm_id, username);


--
-- Name: org_domain ORG_DOMAIN_pkey; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.org_domain
    ADD CONSTRAINT "ORG_DOMAIN_pkey" PRIMARY KEY (id, name);


--
-- Name: org ORG_pkey; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT "ORG_pkey" PRIMARY KEY (id);


--
-- Name: keycloak_role UK_J3RWUVD56ONTGSUHOGM184WW2-2; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT "UK_J3RWUVD56ONTGSUHOGM184WW2-2" UNIQUE (name, client_realm_constraint);


--
-- Name: client_auth_flow_bindings c_cli_flow_bind; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_auth_flow_bindings
    ADD CONSTRAINT c_cli_flow_bind PRIMARY KEY (client_id, binding_name);


--
-- Name: client_scope_client c_cli_scope_bind; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope_client
    ADD CONSTRAINT c_cli_scope_bind PRIMARY KEY (client_id, scope_id);


--
-- Name: client_initial_access cnstr_client_init_acc_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_initial_access
    ADD CONSTRAINT cnstr_client_init_acc_pk PRIMARY KEY (id);


--
-- Name: realm_default_groups con_group_id_def_groups; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT con_group_id_def_groups UNIQUE (group_id);


--
-- Name: broker_link constr_broker_link_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.broker_link
    ADD CONSTRAINT constr_broker_link_pk PRIMARY KEY (identity_provider, user_id);


--
-- Name: client_user_session_note constr_cl_usr_ses_note; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_user_session_note
    ADD CONSTRAINT constr_cl_usr_ses_note PRIMARY KEY (client_session, name);


--
-- Name: component_config constr_component_config_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.component_config
    ADD CONSTRAINT constr_component_config_pk PRIMARY KEY (id);


--
-- Name: component constr_component_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.component
    ADD CONSTRAINT constr_component_pk PRIMARY KEY (id);


--
-- Name: fed_user_required_action constr_fed_required_action; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_required_action
    ADD CONSTRAINT constr_fed_required_action PRIMARY KEY (required_action, user_id);


--
-- Name: fed_user_attribute constr_fed_user_attr_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_attribute
    ADD CONSTRAINT constr_fed_user_attr_pk PRIMARY KEY (id);


--
-- Name: fed_user_consent constr_fed_user_consent_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_consent
    ADD CONSTRAINT constr_fed_user_consent_pk PRIMARY KEY (id);


--
-- Name: fed_user_credential constr_fed_user_cred_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_credential
    ADD CONSTRAINT constr_fed_user_cred_pk PRIMARY KEY (id);


--
-- Name: fed_user_group_membership constr_fed_user_group; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_group_membership
    ADD CONSTRAINT constr_fed_user_group PRIMARY KEY (group_id, user_id);


--
-- Name: fed_user_role_mapping constr_fed_user_role; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_role_mapping
    ADD CONSTRAINT constr_fed_user_role PRIMARY KEY (role_id, user_id);


--
-- Name: federated_user constr_federated_user; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.federated_user
    ADD CONSTRAINT constr_federated_user PRIMARY KEY (id);


--
-- Name: realm_default_groups constr_realm_default_groups; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT constr_realm_default_groups PRIMARY KEY (realm_id, group_id);


--
-- Name: realm_enabled_event_types constr_realm_enabl_event_types; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_enabled_event_types
    ADD CONSTRAINT constr_realm_enabl_event_types PRIMARY KEY (realm_id, value);


--
-- Name: realm_events_listeners constr_realm_events_listeners; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_events_listeners
    ADD CONSTRAINT constr_realm_events_listeners PRIMARY KEY (realm_id, value);


--
-- Name: realm_supported_locales constr_realm_supported_locales; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_supported_locales
    ADD CONSTRAINT constr_realm_supported_locales PRIMARY KEY (realm_id, value);


--
-- Name: identity_provider constraint_2b; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT constraint_2b PRIMARY KEY (internal_id);


--
-- Name: client_attributes constraint_3c; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_attributes
    ADD CONSTRAINT constraint_3c PRIMARY KEY (client_id, name);


--
-- Name: event_entity constraint_4; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.event_entity
    ADD CONSTRAINT constraint_4 PRIMARY KEY (id);


--
-- Name: federated_identity constraint_40; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.federated_identity
    ADD CONSTRAINT constraint_40 PRIMARY KEY (identity_provider, user_id);


--
-- Name: realm constraint_4a; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm
    ADD CONSTRAINT constraint_4a PRIMARY KEY (id);


--
-- Name: client_session_role constraint_5; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_role
    ADD CONSTRAINT constraint_5 PRIMARY KEY (client_session, role_id);


--
-- Name: user_session constraint_57; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_session
    ADD CONSTRAINT constraint_57 PRIMARY KEY (id);


--
-- Name: user_federation_provider constraint_5c; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_provider
    ADD CONSTRAINT constraint_5c PRIMARY KEY (id);


--
-- Name: client_session_note constraint_5e; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_note
    ADD CONSTRAINT constraint_5e PRIMARY KEY (client_session, name);


--
-- Name: client constraint_7; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT constraint_7 PRIMARY KEY (id);


--
-- Name: client_session constraint_8; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session
    ADD CONSTRAINT constraint_8 PRIMARY KEY (id);


--
-- Name: scope_mapping constraint_81; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.scope_mapping
    ADD CONSTRAINT constraint_81 PRIMARY KEY (client_id, role_id);


--
-- Name: client_node_registrations constraint_84; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_node_registrations
    ADD CONSTRAINT constraint_84 PRIMARY KEY (client_id, name);


--
-- Name: realm_attribute constraint_9; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_attribute
    ADD CONSTRAINT constraint_9 PRIMARY KEY (name, realm_id);


--
-- Name: realm_required_credential constraint_92; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_required_credential
    ADD CONSTRAINT constraint_92 PRIMARY KEY (realm_id, type);


--
-- Name: keycloak_role constraint_a; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT constraint_a PRIMARY KEY (id);


--
-- Name: admin_event_entity constraint_admin_event_entity; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.admin_event_entity
    ADD CONSTRAINT constraint_admin_event_entity PRIMARY KEY (id);


--
-- Name: authenticator_config_entry constraint_auth_cfg_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authenticator_config_entry
    ADD CONSTRAINT constraint_auth_cfg_pk PRIMARY KEY (authenticator_id, name);


--
-- Name: authentication_execution constraint_auth_exec_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT constraint_auth_exec_pk PRIMARY KEY (id);


--
-- Name: authentication_flow constraint_auth_flow_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authentication_flow
    ADD CONSTRAINT constraint_auth_flow_pk PRIMARY KEY (id);


--
-- Name: authenticator_config constraint_auth_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authenticator_config
    ADD CONSTRAINT constraint_auth_pk PRIMARY KEY (id);


--
-- Name: client_session_auth_status constraint_auth_status_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_auth_status
    ADD CONSTRAINT constraint_auth_status_pk PRIMARY KEY (client_session, authenticator);


--
-- Name: user_role_mapping constraint_c; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT constraint_c PRIMARY KEY (role_id, user_id);


--
-- Name: composite_role constraint_composite_role; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT constraint_composite_role PRIMARY KEY (composite, child_role);


--
-- Name: client_session_prot_mapper constraint_cs_pmp_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_prot_mapper
    ADD CONSTRAINT constraint_cs_pmp_pk PRIMARY KEY (client_session, protocol_mapper_id);


--
-- Name: identity_provider_config constraint_d; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider_config
    ADD CONSTRAINT constraint_d PRIMARY KEY (identity_provider_id, name);


--
-- Name: policy_config constraint_dpc; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.policy_config
    ADD CONSTRAINT constraint_dpc PRIMARY KEY (policy_id, name);


--
-- Name: realm_smtp_config constraint_e; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_smtp_config
    ADD CONSTRAINT constraint_e PRIMARY KEY (realm_id, name);


--
-- Name: credential constraint_f; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.credential
    ADD CONSTRAINT constraint_f PRIMARY KEY (id);


--
-- Name: user_federation_config constraint_f9; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_config
    ADD CONSTRAINT constraint_f9 PRIMARY KEY (user_federation_provider_id, name);


--
-- Name: resource_server_perm_ticket constraint_fapmt; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT constraint_fapmt PRIMARY KEY (id);


--
-- Name: resource_server_resource constraint_farsr; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT constraint_farsr PRIMARY KEY (id);


--
-- Name: resource_server_policy constraint_farsrp; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT constraint_farsrp PRIMARY KEY (id);


--
-- Name: associated_policy constraint_farsrpap; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT constraint_farsrpap PRIMARY KEY (policy_id, associated_policy_id);


--
-- Name: resource_policy constraint_farsrpp; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT constraint_farsrpp PRIMARY KEY (resource_id, policy_id);


--
-- Name: resource_server_scope constraint_farsrs; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT constraint_farsrs PRIMARY KEY (id);


--
-- Name: resource_scope constraint_farsrsp; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT constraint_farsrsp PRIMARY KEY (resource_id, scope_id);


--
-- Name: scope_policy constraint_farsrsps; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT constraint_farsrsps PRIMARY KEY (scope_id, policy_id);


--
-- Name: user_entity constraint_fb; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT constraint_fb PRIMARY KEY (id);


--
-- Name: user_federation_mapper_config constraint_fedmapper_cfg_pm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_mapper_config
    ADD CONSTRAINT constraint_fedmapper_cfg_pm PRIMARY KEY (user_federation_mapper_id, name);


--
-- Name: user_federation_mapper constraint_fedmapperpm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT constraint_fedmapperpm PRIMARY KEY (id);


--
-- Name: fed_user_consent_cl_scope constraint_fgrntcsnt_clsc_pm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.fed_user_consent_cl_scope
    ADD CONSTRAINT constraint_fgrntcsnt_clsc_pm PRIMARY KEY (user_consent_id, scope_id);


--
-- Name: user_consent_client_scope constraint_grntcsnt_clsc_pm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent_client_scope
    ADD CONSTRAINT constraint_grntcsnt_clsc_pm PRIMARY KEY (user_consent_id, scope_id);


--
-- Name: user_consent constraint_grntcsnt_pm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT constraint_grntcsnt_pm PRIMARY KEY (id);


--
-- Name: keycloak_group constraint_group; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.keycloak_group
    ADD CONSTRAINT constraint_group PRIMARY KEY (id);


--
-- Name: group_attribute constraint_group_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.group_attribute
    ADD CONSTRAINT constraint_group_attribute_pk PRIMARY KEY (id);


--
-- Name: group_role_mapping constraint_group_role; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.group_role_mapping
    ADD CONSTRAINT constraint_group_role PRIMARY KEY (role_id, group_id);


--
-- Name: identity_provider_mapper constraint_idpm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider_mapper
    ADD CONSTRAINT constraint_idpm PRIMARY KEY (id);


--
-- Name: idp_mapper_config constraint_idpmconfig; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.idp_mapper_config
    ADD CONSTRAINT constraint_idpmconfig PRIMARY KEY (idp_mapper_id, name);


--
-- Name: migration_model constraint_migmod; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.migration_model
    ADD CONSTRAINT constraint_migmod PRIMARY KEY (id);


--
-- Name: offline_client_session constraint_offl_cl_ses_pk3; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.offline_client_session
    ADD CONSTRAINT constraint_offl_cl_ses_pk3 PRIMARY KEY (user_session_id, client_id, client_storage_provider, external_client_id, offline_flag);


--
-- Name: offline_user_session constraint_offl_us_ses_pk2; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.offline_user_session
    ADD CONSTRAINT constraint_offl_us_ses_pk2 PRIMARY KEY (user_session_id, offline_flag);


--
-- Name: protocol_mapper constraint_pcm; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT constraint_pcm PRIMARY KEY (id);


--
-- Name: protocol_mapper_config constraint_pmconfig; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.protocol_mapper_config
    ADD CONSTRAINT constraint_pmconfig PRIMARY KEY (protocol_mapper_id, name);


--
-- Name: redirect_uris constraint_redirect_uris; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.redirect_uris
    ADD CONSTRAINT constraint_redirect_uris PRIMARY KEY (client_id, value);


--
-- Name: required_action_config constraint_req_act_cfg_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.required_action_config
    ADD CONSTRAINT constraint_req_act_cfg_pk PRIMARY KEY (required_action_id, name);


--
-- Name: required_action_provider constraint_req_act_prv_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.required_action_provider
    ADD CONSTRAINT constraint_req_act_prv_pk PRIMARY KEY (id);


--
-- Name: user_required_action constraint_required_action; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_required_action
    ADD CONSTRAINT constraint_required_action PRIMARY KEY (required_action, user_id);


--
-- Name: resource_uris constraint_resour_uris_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_uris
    ADD CONSTRAINT constraint_resour_uris_pk PRIMARY KEY (resource_id, value);


--
-- Name: role_attribute constraint_role_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.role_attribute
    ADD CONSTRAINT constraint_role_attribute_pk PRIMARY KEY (id);


--
-- Name: user_attribute constraint_user_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_attribute
    ADD CONSTRAINT constraint_user_attribute_pk PRIMARY KEY (id);


--
-- Name: user_group_membership constraint_user_group; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_group_membership
    ADD CONSTRAINT constraint_user_group PRIMARY KEY (group_id, user_id);


--
-- Name: user_session_note constraint_usn_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_session_note
    ADD CONSTRAINT constraint_usn_pk PRIMARY KEY (user_session, name);


--
-- Name: web_origins constraint_web_origins; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.web_origins
    ADD CONSTRAINT constraint_web_origins PRIMARY KEY (client_id, value);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: client_scope_attributes pk_cl_tmpl_attr; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope_attributes
    ADD CONSTRAINT pk_cl_tmpl_attr PRIMARY KEY (scope_id, name);


--
-- Name: client_scope pk_cli_template; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope
    ADD CONSTRAINT pk_cli_template PRIMARY KEY (id);


--
-- Name: resource_server pk_resource_server; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server
    ADD CONSTRAINT pk_resource_server PRIMARY KEY (id);


--
-- Name: client_scope_role_mapping pk_template_scope; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope_role_mapping
    ADD CONSTRAINT pk_template_scope PRIMARY KEY (scope_id, role_id);


--
-- Name: default_client_scope r_def_cli_scope_bind; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.default_client_scope
    ADD CONSTRAINT r_def_cli_scope_bind PRIMARY KEY (realm_id, scope_id);


--
-- Name: realm_localizations realm_localizations_pkey; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_localizations
    ADD CONSTRAINT realm_localizations_pkey PRIMARY KEY (realm_id, locale);


--
-- Name: resource_attribute res_attr_pk; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_attribute
    ADD CONSTRAINT res_attr_pk PRIMARY KEY (id);


--
-- Name: keycloak_group sibling_names; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.keycloak_group
    ADD CONSTRAINT sibling_names UNIQUE (realm_id, parent_group, name);


--
-- Name: identity_provider uk_2daelwnibji49avxsrtuf6xj33; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT uk_2daelwnibji49avxsrtuf6xj33 UNIQUE (provider_alias, realm_id);


--
-- Name: client uk_b71cjlbenv945rb6gcon438at; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT uk_b71cjlbenv945rb6gcon438at UNIQUE (realm_id, client_id);


--
-- Name: client_scope uk_cli_scope; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope
    ADD CONSTRAINT uk_cli_scope UNIQUE (realm_id, name);


--
-- Name: user_entity uk_dykn684sl8up1crfei6eckhd7; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT uk_dykn684sl8up1crfei6eckhd7 UNIQUE (realm_id, email_constraint);


--
-- Name: user_consent uk_external_consent; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT uk_external_consent UNIQUE (client_storage_provider, external_client_id, user_id);


--
-- Name: resource_server_resource uk_frsr6t700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT uk_frsr6t700s9v50bu18ws5ha6 UNIQUE (name, owner, resource_server_id);


--
-- Name: resource_server_perm_ticket uk_frsr6t700s9v50bu18ws5pmt; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT uk_frsr6t700s9v50bu18ws5pmt UNIQUE (owner, requester, resource_server_id, resource_id, scope_id);


--
-- Name: resource_server_policy uk_frsrpt700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT uk_frsrpt700s9v50bu18ws5ha6 UNIQUE (name, resource_server_id);


--
-- Name: resource_server_scope uk_frsrst700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT uk_frsrst700s9v50bu18ws5ha6 UNIQUE (name, resource_server_id);


--
-- Name: user_consent uk_local_consent; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT uk_local_consent UNIQUE (client_id, user_id);


--
-- Name: org uk_org_group; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT uk_org_group UNIQUE (group_id);


--
-- Name: org uk_org_name; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT uk_org_name UNIQUE (realm_id, name);


--
-- Name: realm uk_orvsdmla56612eaefiq6wl5oi; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm
    ADD CONSTRAINT uk_orvsdmla56612eaefiq6wl5oi UNIQUE (name);


--
-- Name: user_entity uk_ru8tt6t700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT uk_ru8tt6t700s9v50bu18ws5ha6 UNIQUE (realm_id, username);


--
-- Name: fed_user_attr_long_values; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX fed_user_attr_long_values ON public.fed_user_attribute USING btree (long_value_hash, name);


--
-- Name: fed_user_attr_long_values_lower_case; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX fed_user_attr_long_values_lower_case ON public.fed_user_attribute USING btree (long_value_hash_lower_case, name);


--
-- Name: idx_admin_event_time; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_admin_event_time ON public.admin_event_entity USING btree (realm_id, admin_event_time);


--
-- Name: idx_assoc_pol_assoc_pol_id; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_assoc_pol_assoc_pol_id ON public.associated_policy USING btree (associated_policy_id);


--
-- Name: idx_auth_config_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_auth_config_realm ON public.authenticator_config USING btree (realm_id);


--
-- Name: idx_auth_exec_flow; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_auth_exec_flow ON public.authentication_execution USING btree (flow_id);


--
-- Name: idx_auth_exec_realm_flow; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_auth_exec_realm_flow ON public.authentication_execution USING btree (realm_id, flow_id);


--
-- Name: idx_auth_flow_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_auth_flow_realm ON public.authentication_flow USING btree (realm_id);


--
-- Name: idx_cl_clscope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_cl_clscope ON public.client_scope_client USING btree (scope_id);


--
-- Name: idx_client_att_by_name_value; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_client_att_by_name_value ON public.client_attributes USING btree (name, substr(value, 1, 255));


--
-- Name: idx_client_id; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_client_id ON public.client USING btree (client_id);


--
-- Name: idx_client_init_acc_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_client_init_acc_realm ON public.client_initial_access USING btree (realm_id);


--
-- Name: idx_client_session_session; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_client_session_session ON public.client_session USING btree (session_id);


--
-- Name: idx_clscope_attrs; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_clscope_attrs ON public.client_scope_attributes USING btree (scope_id);


--
-- Name: idx_clscope_cl; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_clscope_cl ON public.client_scope_client USING btree (client_id);


--
-- Name: idx_clscope_protmap; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_clscope_protmap ON public.protocol_mapper USING btree (client_scope_id);


--
-- Name: idx_clscope_role; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_clscope_role ON public.client_scope_role_mapping USING btree (scope_id);


--
-- Name: idx_compo_config_compo; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_compo_config_compo ON public.component_config USING btree (component_id);


--
-- Name: idx_component_provider_type; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_component_provider_type ON public.component USING btree (provider_type);


--
-- Name: idx_component_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_component_realm ON public.component USING btree (realm_id);


--
-- Name: idx_composite; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_composite ON public.composite_role USING btree (composite);


--
-- Name: idx_composite_child; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_composite_child ON public.composite_role USING btree (child_role);


--
-- Name: idx_defcls_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_defcls_realm ON public.default_client_scope USING btree (realm_id);


--
-- Name: idx_defcls_scope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_defcls_scope ON public.default_client_scope USING btree (scope_id);


--
-- Name: idx_event_time; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_event_time ON public.event_entity USING btree (realm_id, event_time);


--
-- Name: idx_fedidentity_feduser; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fedidentity_feduser ON public.federated_identity USING btree (federated_user_id);


--
-- Name: idx_fedidentity_user; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fedidentity_user ON public.federated_identity USING btree (user_id);


--
-- Name: idx_fu_attribute; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_attribute ON public.fed_user_attribute USING btree (user_id, realm_id, name);


--
-- Name: idx_fu_cnsnt_ext; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_cnsnt_ext ON public.fed_user_consent USING btree (user_id, client_storage_provider, external_client_id);


--
-- Name: idx_fu_consent; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_consent ON public.fed_user_consent USING btree (user_id, client_id);


--
-- Name: idx_fu_consent_ru; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_consent_ru ON public.fed_user_consent USING btree (realm_id, user_id);


--
-- Name: idx_fu_credential; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_credential ON public.fed_user_credential USING btree (user_id, type);


--
-- Name: idx_fu_credential_ru; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_credential_ru ON public.fed_user_credential USING btree (realm_id, user_id);


--
-- Name: idx_fu_group_membership; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_group_membership ON public.fed_user_group_membership USING btree (user_id, group_id);


--
-- Name: idx_fu_group_membership_ru; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_group_membership_ru ON public.fed_user_group_membership USING btree (realm_id, user_id);


--
-- Name: idx_fu_required_action; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_required_action ON public.fed_user_required_action USING btree (user_id, required_action);


--
-- Name: idx_fu_required_action_ru; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_required_action_ru ON public.fed_user_required_action USING btree (realm_id, user_id);


--
-- Name: idx_fu_role_mapping; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_role_mapping ON public.fed_user_role_mapping USING btree (user_id, role_id);


--
-- Name: idx_fu_role_mapping_ru; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_fu_role_mapping_ru ON public.fed_user_role_mapping USING btree (realm_id, user_id);


--
-- Name: idx_group_att_by_name_value; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_group_att_by_name_value ON public.group_attribute USING btree (name, ((value)::character varying(250)));


--
-- Name: idx_group_attr_group; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_group_attr_group ON public.group_attribute USING btree (group_id);


--
-- Name: idx_group_role_mapp_group; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_group_role_mapp_group ON public.group_role_mapping USING btree (group_id);


--
-- Name: idx_id_prov_mapp_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_id_prov_mapp_realm ON public.identity_provider_mapper USING btree (realm_id);


--
-- Name: idx_ident_prov_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_ident_prov_realm ON public.identity_provider USING btree (realm_id);


--
-- Name: idx_keycloak_role_client; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_keycloak_role_client ON public.keycloak_role USING btree (client);


--
-- Name: idx_keycloak_role_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_keycloak_role_realm ON public.keycloak_role USING btree (realm);


--
-- Name: idx_offline_uss_by_broker_session_id; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_offline_uss_by_broker_session_id ON public.offline_user_session USING btree (broker_session_id, realm_id);


--
-- Name: idx_offline_uss_by_last_session_refresh; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_offline_uss_by_last_session_refresh ON public.offline_user_session USING btree (realm_id, offline_flag, last_session_refresh);


--
-- Name: idx_offline_uss_by_user; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_offline_uss_by_user ON public.offline_user_session USING btree (user_id, realm_id, offline_flag);


--
-- Name: idx_perm_ticket_owner; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_perm_ticket_owner ON public.resource_server_perm_ticket USING btree (owner);


--
-- Name: idx_perm_ticket_requester; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_perm_ticket_requester ON public.resource_server_perm_ticket USING btree (requester);


--
-- Name: idx_protocol_mapper_client; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_protocol_mapper_client ON public.protocol_mapper USING btree (client_id);


--
-- Name: idx_realm_attr_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_attr_realm ON public.realm_attribute USING btree (realm_id);


--
-- Name: idx_realm_clscope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_clscope ON public.client_scope USING btree (realm_id);


--
-- Name: idx_realm_def_grp_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_def_grp_realm ON public.realm_default_groups USING btree (realm_id);


--
-- Name: idx_realm_evt_list_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_evt_list_realm ON public.realm_events_listeners USING btree (realm_id);


--
-- Name: idx_realm_evt_types_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_evt_types_realm ON public.realm_enabled_event_types USING btree (realm_id);


--
-- Name: idx_realm_master_adm_cli; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_master_adm_cli ON public.realm USING btree (master_admin_client);


--
-- Name: idx_realm_supp_local_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_realm_supp_local_realm ON public.realm_supported_locales USING btree (realm_id);


--
-- Name: idx_redir_uri_client; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_redir_uri_client ON public.redirect_uris USING btree (client_id);


--
-- Name: idx_req_act_prov_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_req_act_prov_realm ON public.required_action_provider USING btree (realm_id);


--
-- Name: idx_res_policy_policy; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_res_policy_policy ON public.resource_policy USING btree (policy_id);


--
-- Name: idx_res_scope_scope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_res_scope_scope ON public.resource_scope USING btree (scope_id);


--
-- Name: idx_res_serv_pol_res_serv; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_res_serv_pol_res_serv ON public.resource_server_policy USING btree (resource_server_id);


--
-- Name: idx_res_srv_res_res_srv; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_res_srv_res_res_srv ON public.resource_server_resource USING btree (resource_server_id);


--
-- Name: idx_res_srv_scope_res_srv; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_res_srv_scope_res_srv ON public.resource_server_scope USING btree (resource_server_id);


--
-- Name: idx_role_attribute; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_role_attribute ON public.role_attribute USING btree (role_id);


--
-- Name: idx_role_clscope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_role_clscope ON public.client_scope_role_mapping USING btree (role_id);


--
-- Name: idx_scope_mapping_role; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_scope_mapping_role ON public.scope_mapping USING btree (role_id);


--
-- Name: idx_scope_policy_policy; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_scope_policy_policy ON public.scope_policy USING btree (policy_id);


--
-- Name: idx_update_time; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_update_time ON public.migration_model USING btree (update_time);


--
-- Name: idx_us_sess_id_on_cl_sess; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_us_sess_id_on_cl_sess ON public.offline_client_session USING btree (user_session_id);


--
-- Name: idx_usconsent_clscope; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_usconsent_clscope ON public.user_consent_client_scope USING btree (user_consent_id);


--
-- Name: idx_usconsent_scope_id; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_usconsent_scope_id ON public.user_consent_client_scope USING btree (scope_id);


--
-- Name: idx_user_attribute; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_attribute ON public.user_attribute USING btree (user_id);


--
-- Name: idx_user_attribute_name; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_attribute_name ON public.user_attribute USING btree (name, value);


--
-- Name: idx_user_consent; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_consent ON public.user_consent USING btree (user_id);


--
-- Name: idx_user_credential; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_credential ON public.credential USING btree (user_id);


--
-- Name: idx_user_email; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_email ON public.user_entity USING btree (email);


--
-- Name: idx_user_group_mapping; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_group_mapping ON public.user_group_membership USING btree (user_id);


--
-- Name: idx_user_reqactions; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_reqactions ON public.user_required_action USING btree (user_id);


--
-- Name: idx_user_role_mapping; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_role_mapping ON public.user_role_mapping USING btree (user_id);


--
-- Name: idx_user_service_account; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_user_service_account ON public.user_entity USING btree (realm_id, service_account_client_link);


--
-- Name: idx_usr_fed_map_fed_prv; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_usr_fed_map_fed_prv ON public.user_federation_mapper USING btree (federation_provider_id);


--
-- Name: idx_usr_fed_map_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_usr_fed_map_realm ON public.user_federation_mapper USING btree (realm_id);


--
-- Name: idx_usr_fed_prv_realm; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_usr_fed_prv_realm ON public.user_federation_provider USING btree (realm_id);


--
-- Name: idx_web_orig_client; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX idx_web_orig_client ON public.web_origins USING btree (client_id);


--
-- Name: user_attr_long_values; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX user_attr_long_values ON public.user_attribute USING btree (long_value_hash, name);


--
-- Name: user_attr_long_values_lower_case; Type: INDEX; Schema: public; Owner: keycloak_user
--

CREATE INDEX user_attr_long_values_lower_case ON public.user_attribute USING btree (long_value_hash_lower_case, name);


--
-- Name: client_session_auth_status auth_status_constraint; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_auth_status
    ADD CONSTRAINT auth_status_constraint FOREIGN KEY (client_session) REFERENCES public.client_session(id);


--
-- Name: identity_provider fk2b4ebc52ae5c3b34; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT fk2b4ebc52ae5c3b34 FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: client_attributes fk3c47c64beacca966; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_attributes
    ADD CONSTRAINT fk3c47c64beacca966 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: federated_identity fk404288b92ef007a6; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.federated_identity
    ADD CONSTRAINT fk404288b92ef007a6 FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: client_node_registrations fk4129723ba992f594; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_node_registrations
    ADD CONSTRAINT fk4129723ba992f594 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: client_session_note fk5edfb00ff51c2736; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_note
    ADD CONSTRAINT fk5edfb00ff51c2736 FOREIGN KEY (client_session) REFERENCES public.client_session(id);


--
-- Name: user_session_note fk5edfb00ff51d3472; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_session_note
    ADD CONSTRAINT fk5edfb00ff51d3472 FOREIGN KEY (user_session) REFERENCES public.user_session(id);


--
-- Name: client_session_role fk_11b7sgqw18i532811v7o2dv76; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_role
    ADD CONSTRAINT fk_11b7sgqw18i532811v7o2dv76 FOREIGN KEY (client_session) REFERENCES public.client_session(id);


--
-- Name: redirect_uris fk_1burs8pb4ouj97h5wuppahv9f; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.redirect_uris
    ADD CONSTRAINT fk_1burs8pb4ouj97h5wuppahv9f FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: user_federation_provider fk_1fj32f6ptolw2qy60cd8n01e8; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_provider
    ADD CONSTRAINT fk_1fj32f6ptolw2qy60cd8n01e8 FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: client_session_prot_mapper fk_33a8sgqw18i532811v7o2dk89; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session_prot_mapper
    ADD CONSTRAINT fk_33a8sgqw18i532811v7o2dk89 FOREIGN KEY (client_session) REFERENCES public.client_session(id);


--
-- Name: realm_required_credential fk_5hg65lybevavkqfki3kponh9v; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_required_credential
    ADD CONSTRAINT fk_5hg65lybevavkqfki3kponh9v FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: resource_attribute fk_5hrm2vlf9ql5fu022kqepovbr; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_attribute
    ADD CONSTRAINT fk_5hrm2vlf9ql5fu022kqepovbr FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: user_attribute fk_5hrm2vlf9ql5fu043kqepovbr; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_attribute
    ADD CONSTRAINT fk_5hrm2vlf9ql5fu043kqepovbr FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: user_required_action fk_6qj3w1jw9cvafhe19bwsiuvmd; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_required_action
    ADD CONSTRAINT fk_6qj3w1jw9cvafhe19bwsiuvmd FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: keycloak_role fk_6vyqfe4cn4wlq8r6kt5vdsj5c; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT fk_6vyqfe4cn4wlq8r6kt5vdsj5c FOREIGN KEY (realm) REFERENCES public.realm(id);


--
-- Name: realm_smtp_config fk_70ej8xdxgxd0b9hh6180irr0o; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_smtp_config
    ADD CONSTRAINT fk_70ej8xdxgxd0b9hh6180irr0o FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_attribute fk_8shxd6l3e9atqukacxgpffptw; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_attribute
    ADD CONSTRAINT fk_8shxd6l3e9atqukacxgpffptw FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: composite_role fk_a63wvekftu8jo1pnj81e7mce2; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT fk_a63wvekftu8jo1pnj81e7mce2 FOREIGN KEY (composite) REFERENCES public.keycloak_role(id);


--
-- Name: authentication_execution fk_auth_exec_flow; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT fk_auth_exec_flow FOREIGN KEY (flow_id) REFERENCES public.authentication_flow(id);


--
-- Name: authentication_execution fk_auth_exec_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT fk_auth_exec_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: authentication_flow fk_auth_flow_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authentication_flow
    ADD CONSTRAINT fk_auth_flow_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: authenticator_config fk_auth_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.authenticator_config
    ADD CONSTRAINT fk_auth_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: client_session fk_b4ao2vcvat6ukau74wbwtfqo1; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_session
    ADD CONSTRAINT fk_b4ao2vcvat6ukau74wbwtfqo1 FOREIGN KEY (session_id) REFERENCES public.user_session(id);


--
-- Name: user_role_mapping fk_c4fqv34p1mbylloxang7b1q3l; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT fk_c4fqv34p1mbylloxang7b1q3l FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: client_scope_attributes fk_cl_scope_attr_scope; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope_attributes
    ADD CONSTRAINT fk_cl_scope_attr_scope FOREIGN KEY (scope_id) REFERENCES public.client_scope(id);


--
-- Name: client_scope_role_mapping fk_cl_scope_rm_scope; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_scope_role_mapping
    ADD CONSTRAINT fk_cl_scope_rm_scope FOREIGN KEY (scope_id) REFERENCES public.client_scope(id);


--
-- Name: client_user_session_note fk_cl_usr_ses_note; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_user_session_note
    ADD CONSTRAINT fk_cl_usr_ses_note FOREIGN KEY (client_session) REFERENCES public.client_session(id);


--
-- Name: protocol_mapper fk_cli_scope_mapper; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT fk_cli_scope_mapper FOREIGN KEY (client_scope_id) REFERENCES public.client_scope(id);


--
-- Name: client_initial_access fk_client_init_acc_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.client_initial_access
    ADD CONSTRAINT fk_client_init_acc_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: component_config fk_component_config; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.component_config
    ADD CONSTRAINT fk_component_config FOREIGN KEY (component_id) REFERENCES public.component(id);


--
-- Name: component fk_component_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.component
    ADD CONSTRAINT fk_component_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_default_groups fk_def_groups_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT fk_def_groups_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: user_federation_mapper_config fk_fedmapper_cfg; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_mapper_config
    ADD CONSTRAINT fk_fedmapper_cfg FOREIGN KEY (user_federation_mapper_id) REFERENCES public.user_federation_mapper(id);


--
-- Name: user_federation_mapper fk_fedmapperpm_fedprv; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT fk_fedmapperpm_fedprv FOREIGN KEY (federation_provider_id) REFERENCES public.user_federation_provider(id);


--
-- Name: user_federation_mapper fk_fedmapperpm_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT fk_fedmapperpm_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: associated_policy fk_frsr5s213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT fk_frsr5s213xcx4wnkog82ssrfy FOREIGN KEY (associated_policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: scope_policy fk_frsrasp13xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT fk_frsrasp13xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog82sspmt; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog82sspmt FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_server_resource fk_frsrho213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT fk_frsrho213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog83sspmt; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog83sspmt FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog84sspmt; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog84sspmt FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: associated_policy fk_frsrpas14xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT fk_frsrpas14xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: scope_policy fk_frsrpass3xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT fk_frsrpass3xcx4wnkog82ssrfy FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: resource_server_perm_ticket fk_frsrpo2128cx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrpo2128cx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_server_policy fk_frsrpo213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT fk_frsrpo213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_scope fk_frsrpos13xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT fk_frsrpos13xcx4wnkog82ssrfy FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_policy fk_frsrpos53xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT fk_frsrpos53xcx4wnkog82ssrfy FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_policy fk_frsrpp213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT fk_frsrpp213xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_scope fk_frsrps213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT fk_frsrps213xcx4wnkog82ssrfy FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: resource_server_scope fk_frsrso213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT fk_frsrso213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: composite_role fk_gr7thllb9lu8q4vqa4524jjy8; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT fk_gr7thllb9lu8q4vqa4524jjy8 FOREIGN KEY (child_role) REFERENCES public.keycloak_role(id);


--
-- Name: user_consent_client_scope fk_grntcsnt_clsc_usc; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent_client_scope
    ADD CONSTRAINT fk_grntcsnt_clsc_usc FOREIGN KEY (user_consent_id) REFERENCES public.user_consent(id);


--
-- Name: user_consent fk_grntcsnt_user; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT fk_grntcsnt_user FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: group_attribute fk_group_attribute_group; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.group_attribute
    ADD CONSTRAINT fk_group_attribute_group FOREIGN KEY (group_id) REFERENCES public.keycloak_group(id);


--
-- Name: group_role_mapping fk_group_role_group; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.group_role_mapping
    ADD CONSTRAINT fk_group_role_group FOREIGN KEY (group_id) REFERENCES public.keycloak_group(id);


--
-- Name: realm_enabled_event_types fk_h846o4h0w8epx5nwedrf5y69j; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_enabled_event_types
    ADD CONSTRAINT fk_h846o4h0w8epx5nwedrf5y69j FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_events_listeners fk_h846o4h0w8epx5nxev9f5y69j; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_events_listeners
    ADD CONSTRAINT fk_h846o4h0w8epx5nxev9f5y69j FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: identity_provider_mapper fk_idpm_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider_mapper
    ADD CONSTRAINT fk_idpm_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: idp_mapper_config fk_idpmconfig; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.idp_mapper_config
    ADD CONSTRAINT fk_idpmconfig FOREIGN KEY (idp_mapper_id) REFERENCES public.identity_provider_mapper(id);


--
-- Name: web_origins fk_lojpho213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.web_origins
    ADD CONSTRAINT fk_lojpho213xcx4wnkog82ssrfy FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: scope_mapping fk_ouse064plmlr732lxjcn1q5f1; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.scope_mapping
    ADD CONSTRAINT fk_ouse064plmlr732lxjcn1q5f1 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: protocol_mapper fk_pcm_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT fk_pcm_realm FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: credential fk_pfyr0glasqyl0dei3kl69r6v0; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.credential
    ADD CONSTRAINT fk_pfyr0glasqyl0dei3kl69r6v0 FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: protocol_mapper_config fk_pmconfig; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.protocol_mapper_config
    ADD CONSTRAINT fk_pmconfig FOREIGN KEY (protocol_mapper_id) REFERENCES public.protocol_mapper(id);


--
-- Name: default_client_scope fk_r_def_cli_scope_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.default_client_scope
    ADD CONSTRAINT fk_r_def_cli_scope_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: required_action_provider fk_req_act_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.required_action_provider
    ADD CONSTRAINT fk_req_act_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: resource_uris fk_resource_server_uris; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.resource_uris
    ADD CONSTRAINT fk_resource_server_uris FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: role_attribute fk_role_attribute_id; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.role_attribute
    ADD CONSTRAINT fk_role_attribute_id FOREIGN KEY (role_id) REFERENCES public.keycloak_role(id);


--
-- Name: realm_supported_locales fk_supported_locales_realm; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.realm_supported_locales
    ADD CONSTRAINT fk_supported_locales_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: user_federation_config fk_t13hpu1j94r2ebpekr39x5eu5; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_federation_config
    ADD CONSTRAINT fk_t13hpu1j94r2ebpekr39x5eu5 FOREIGN KEY (user_federation_provider_id) REFERENCES public.user_federation_provider(id);


--
-- Name: user_group_membership fk_user_group_user; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.user_group_membership
    ADD CONSTRAINT fk_user_group_user FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: policy_config fkdc34197cf864c4e43; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.policy_config
    ADD CONSTRAINT fkdc34197cf864c4e43 FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: identity_provider_config fkdc4897cf864c4e43; Type: FK CONSTRAINT; Schema: public; Owner: keycloak_user
--

ALTER TABLE ONLY public.identity_provider_config
    ADD CONSTRAINT fkdc4897cf864c4e43 FOREIGN KEY (identity_provider_id) REFERENCES public.identity_provider(internal_id);


--
-- PostgreSQL database dump complete
--

\unrestrict xm3PGpFXURMOfTQuWLCyp95Rulj9VpXAnzV9psPWTatINIuf8J4nBI8c15iDm5P

