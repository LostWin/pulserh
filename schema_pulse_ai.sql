--
-- PostgreSQL database dump
--

\restrict 70PEbyHXzNmFz1LBEJ06cr6BLAJQtCtWunkwC6nR3xD31O33fI4dy5GCHWvsafw

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
-- Name: ai_configuration; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.ai_configuration (
    id character varying NOT NULL,
    provider character varying,
    model_name character varying,
    temperature double precision,
    max_tokens integer,
    system_prompt text,
    guardrails_enabled boolean,
    updated_by character varying,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.ai_configuration OWNER TO pulse_ai_user;

--
-- Name: ai_observability_events; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.ai_observability_events (
    id character varying NOT NULL,
    user_id character varying,
    event_type character varying NOT NULL,
    status character varying NOT NULL,
    duration_ms integer,
    tokens_used integer,
    details_json json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.ai_observability_events OWNER TO pulse_ai_user;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pulse_ai_user;

--
-- Name: alert_recipient_states; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.alert_recipient_states (
    id character varying NOT NULL,
    alert_id character varying NOT NULL,
    user_id character varying NOT NULL,
    read_at timestamp with time zone,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    status character varying NOT NULL
);


ALTER TABLE public.alert_recipient_states OWNER TO pulse_ai_user;

--
-- Name: alerts; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.alerts (
    id character varying NOT NULL,
    fingerprint character varying NOT NULL,
    type character varying NOT NULL,
    severity character varying NOT NULL,
    title character varying NOT NULL,
    message text,
    status character varying NOT NULL,
    source character varying NOT NULL,
    employee_id character varying,
    workflow_id character varying,
    target_user_id character varying,
    target_roles json,
    link character varying,
    payload json,
    action_plan text,
    resolved_by character varying,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.alerts OWNER TO pulse_ai_user;

--
-- Name: attendances; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.attendances (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    date date NOT NULL,
    check_in timestamp without time zone,
    check_out timestamp without time zone,
    status character varying NOT NULL
);


ALTER TABLE public.attendances OWNER TO pulse_ai_user;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.audit_logs (
    id character varying NOT NULL,
    user_email character varying NOT NULL,
    action character varying NOT NULL,
    log_type character varying NOT NULL,
    ip_address character varying,
    critical boolean,
    "timestamp" timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO pulse_ai_user;

--
-- Name: base_templates; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.base_templates (
    id character varying NOT NULL,
    name character varying NOT NULL,
    html_content text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.base_templates OWNER TO pulse_ai_user;

--
-- Name: benefit_plans; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.benefit_plans (
    id character varying NOT NULL,
    name character varying NOT NULL,
    provider character varying,
    category character varying NOT NULL,
    coverage_summary text,
    enrollment_month integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.benefit_plans OWNER TO pulse_ai_user;

--
-- Name: career_paths; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.career_paths (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    target_job_id character varying,
    target_title character varying NOT NULL,
    readiness_level character varying NOT NULL,
    next_step text,
    mentor_name character varying,
    last_reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.career_paths OWNER TO pulse_ai_user;

--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.chat_messages (
    id character varying NOT NULL,
    conversation_id character varying NOT NULL,
    role character varying NOT NULL,
    content text,
    tool_calls json,
    tool_results json,
    sources json,
    tokens_used integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.chat_messages OWNER TO pulse_ai_user;

--
-- Name: contracts; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.contracts (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    contract_type character varying NOT NULL,
    start_date date NOT NULL,
    end_date date,
    salary double precision NOT NULL,
    is_active boolean
);


ALTER TABLE public.contracts OWNER TO pulse_ai_user;

--
-- Name: conversations; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.conversations (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    title character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.conversations OWNER TO pulse_ai_user;

--
-- Name: data_access_policies; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.data_access_policies (
    id character varying NOT NULL,
    resource character varying NOT NULL,
    scope character varying NOT NULL,
    field_key character varying NOT NULL,
    role character varying NOT NULL,
    visibility character varying DEFAULT 'visible'::character varying NOT NULL,
    mask_type character varying,
    conditions_json json,
    description text,
    updated_by character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.data_access_policies OWNER TO pulse_ai_user;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.departments (
    id character varying NOT NULL,
    name character varying NOT NULL,
    manager_id character varying
);


ALTER TABLE public.departments OWNER TO pulse_ai_user;

--
-- Name: document_access_events; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.document_access_events (
    id character varying NOT NULL,
    document_id character varying NOT NULL,
    user_email character varying NOT NULL,
    action character varying NOT NULL,
    roles json NOT NULL,
    details json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.document_access_events OWNER TO pulse_ai_user;

--
-- Name: document_templates; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.document_templates (
    id character varying NOT NULL,
    name character varying NOT NULL,
    document_type_id character varying NOT NULL,
    base_template_id character varying NOT NULL,
    html_content text NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.document_templates OWNER TO pulse_ai_user;

--
-- Name: document_types; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.document_types (
    id character varying NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL,
    allowed_roles json NOT NULL,
    responsible_role character varying,
    required_variables json NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.document_types OWNER TO pulse_ai_user;

--
-- Name: documents; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.documents (
    id character varying NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    size character varying NOT NULL,
    file_path character varying NOT NULL,
    uploaded_by character varying,
    created_at timestamp with time zone DEFAULT now(),
    allowed_roles json NOT NULL,
    rag_enabled boolean,
    rag_status character varying NOT NULL,
    rag_last_synced_at timestamp with time zone,
    rag_error text,
    status character varying NOT NULL,
    employee_id character varying,
    document_type_id character varying
);


ALTER TABLE public.documents OWNER TO pulse_ai_user;

--
-- Name: employee_benefits; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.employee_benefits (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    benefit_plan_id character varying NOT NULL,
    status character varying NOT NULL,
    effective_date date,
    renewal_date date,
    tier_label character varying,
    employer_contribution double precision,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.employee_benefits OWNER TO pulse_ai_user;

--
-- Name: employee_skills; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.employee_skills (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    skill_id character varying NOT NULL,
    proficiency_level character varying DEFAULT 'intermediate'::character varying NOT NULL,
    years_experience double precision,
    is_primary boolean DEFAULT false,
    last_assessed_at timestamp with time zone,
    source character varying,
    validated_by character varying,
    validated_at timestamp with time zone,
    last_used_at timestamp with time zone,
    confidence_score double precision
);


ALTER TABLE public.employee_skills OWNER TO pulse_ai_user;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.employees (
    id character varying NOT NULL,
    user_id character varying,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    phone character varying,
    hire_date date NOT NULL,
    status character varying,
    department_id character varying,
    job_id character varying,
    manager_id character varying
);


ALTER TABLE public.employees OWNER TO pulse_ai_user;

--
-- Name: engagement_events; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.engagement_events (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    event_type character varying NOT NULL,
    label character varying NOT NULL,
    intensity integer NOT NULL,
    source character varying NOT NULL,
    payload json,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.engagement_events OWNER TO pulse_ai_user;

--
-- Name: engagement_snapshots; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.engagement_snapshots (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    score integer NOT NULL,
    source character varying DEFAULT 'survey'::character varying NOT NULL,
    pulse_label character varying,
    comment text,
    captured_at timestamp with time zone DEFAULT now() NOT NULL,
    trend integer,
    risk_band character varying,
    source_signals json
);


ALTER TABLE public.engagement_snapshots OWNER TO pulse_ai_user;

--
-- Name: generated_reports; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.generated_reports (
    id character varying NOT NULL,
    name character varying NOT NULL,
    period character varying NOT NULL,
    department_filter character varying,
    format character varying DEFAULT 'PDF'::character varying NOT NULL,
    file_path character varying NOT NULL,
    size character varying,
    status character varying DEFAULT 'ready'::character varying NOT NULL,
    created_by character varying NOT NULL,
    meta_json json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.generated_reports OWNER TO pulse_ai_user;

--
-- Name: guardrails; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.guardrails (
    id character varying NOT NULL,
    name character varying NOT NULL,
    pattern character varying NOT NULL,
    action character varying NOT NULL,
    description text,
    is_active boolean,
    priority integer,
    triggered_count integer,
    created_by character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.guardrails OWNER TO pulse_ai_user;

--
-- Name: import_history; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.import_history (
    id character varying NOT NULL,
    filename character varying NOT NULL,
    entity_type character varying NOT NULL,
    processed_lines integer,
    created_lines integer,
    updated_lines integer,
    error_count integer,
    status character varying NOT NULL,
    full_report json,
    created_at timestamp with time zone DEFAULT now(),
    user_id character varying NOT NULL,
    author_name character varying
);


ALTER TABLE public.import_history OWNER TO pulse_ai_user;

--
-- Name: interviews; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.interviews (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    manager_id character varying NOT NULL,
    title character varying DEFAULT 'Entretien individuel'::character varying NOT NULL,
    scheduled_at timestamp with time zone NOT NULL,
    status character varying DEFAULT 'Planifié'::character varying NOT NULL,
    location character varying,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    interview_type character varying NOT NULL,
    duration_minutes integer,
    outcome character varying,
    summary text,
    next_actions json
);


ALTER TABLE public.interviews OWNER TO pulse_ai_user;

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.jobs (
    id character varying NOT NULL,
    title character varying NOT NULL,
    description text,
    level character varying
);


ALTER TABLE public.jobs OWNER TO pulse_ai_user;

--
-- Name: leaves; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.leaves (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    leave_type character varying NOT NULL,
    status character varying,
    reason text
);


ALTER TABLE public.leaves OWNER TO pulse_ai_user;

--
-- Name: mobility_requests; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.mobility_requests (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    target_department_id character varying,
    target_job_id character varying,
    request_type character varying NOT NULL,
    status character varying NOT NULL,
    rationale text,
    requested_at timestamp with time zone DEFAULT now(),
    reviewed_at timestamp with time zone
);


ALTER TABLE public.mobility_requests OWNER TO pulse_ai_user;

--
-- Name: notification_configs; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.notification_configs (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    email_enabled boolean,
    in_app_enabled boolean,
    slack_enabled boolean
);


ALTER TABLE public.notification_configs OWNER TO pulse_ai_user;

--
-- Name: performance_objectives; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.performance_objectives (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    owner_id character varying,
    title character varying NOT NULL,
    description text,
    status character varying NOT NULL,
    progress_pct integer NOT NULL,
    target_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.performance_objectives OWNER TO pulse_ai_user;

--
-- Name: performance_reviews; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.performance_reviews (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    reviewer_id character varying,
    review_type character varying NOT NULL,
    period_label character varying NOT NULL,
    score double precision NOT NULL,
    summary text,
    strengths json,
    improvement_areas json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.performance_reviews OWNER TO pulse_ai_user;

--
-- Name: prediction_snapshots; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.prediction_snapshots (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    prediction_type character varying NOT NULL,
    score double precision NOT NULL,
    level character varying,
    factors_json json,
    model_version character varying,
    computed_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.prediction_snapshots OWNER TO pulse_ai_user;

--
-- Name: project_assignments; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.project_assignments (
    id character varying NOT NULL,
    project_id character varying NOT NULL,
    employee_id character varying NOT NULL,
    role_on_project character varying,
    allocation_pct integer,
    start_date date,
    end_date date,
    is_active boolean DEFAULT true
);


ALTER TABLE public.project_assignments OWNER TO pulse_ai_user;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.projects (
    id character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    start_date date,
    deadline date,
    status character varying,
    priority character varying,
    business_domain character varying,
    required_skill_ids json,
    manager_id character varying
);


ALTER TABLE public.projects OWNER TO pulse_ai_user;

--
-- Name: promotion_history; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.promotion_history (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    previous_job_title character varying,
    new_job_title character varying NOT NULL,
    effective_date date NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.promotion_history OWNER TO pulse_ai_user;

--
-- Name: skills; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.skills (
    id character varying NOT NULL,
    name character varying NOT NULL,
    category character varying,
    description text,
    level_scale character varying,
    is_certifiable boolean,
    is_active boolean
);


ALTER TABLE public.skills OWNER TO pulse_ai_user;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.tasks (
    id character varying NOT NULL,
    project_id character varying NOT NULL,
    assignee_id character varying,
    title character varying NOT NULL,
    description text,
    status character varying,
    due_date date,
    evaluation_score double precision
);


ALTER TABLE public.tasks OWNER TO pulse_ai_user;

--
-- Name: template_assets; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.template_assets (
    id character varying NOT NULL,
    key character varying NOT NULL,
    value text NOT NULL,
    asset_type character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.template_assets OWNER TO pulse_ai_user;

--
-- Name: training_courses; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.training_courses (
    id character varying NOT NULL,
    title character varying NOT NULL,
    provider character varying,
    duration_hours double precision,
    level character varying,
    format character varying,
    description text,
    target_skill_id character varying,
    required_for_job_family character varying,
    difficulty character varying,
    delivery_mode character varying,
    mandatory_for_roles json
);


ALTER TABLE public.training_courses OWNER TO pulse_ai_user;

--
-- Name: training_enrollments; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.training_enrollments (
    id character varying NOT NULL,
    employee_id character varying NOT NULL,
    training_id character varying NOT NULL,
    status character varying DEFAULT 'assigned'::character varying NOT NULL,
    assigned_at timestamp with time zone,
    due_date date,
    completed_at timestamp with time zone,
    score double precision,
    mandatory boolean DEFAULT false,
    assigned_by character varying,
    recommendation_reason text
);


ALTER TABLE public.training_enrollments OWNER TO pulse_ai_user;

--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.user_preferences (
    id character varying NOT NULL,
    user_id character varying NOT NULL,
    avatar_data_url text,
    theme character varying DEFAULT 'dark'::character varying NOT NULL,
    locale character varying DEFAULT 'fr'::character varying NOT NULL,
    timezone character varying DEFAULT 'Africa/Lome'::character varying NOT NULL,
    digest_frequency character varying DEFAULT 'daily'::character varying NOT NULL,
    profile_title character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    birth_date_label character varying,
    address_label text,
    work_location_label character varying
);


ALTER TABLE public.user_preferences OWNER TO pulse_ai_user;

--
-- Name: workflow_steps; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.workflow_steps (
    id character varying NOT NULL,
    workflow_id character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    assigned_to character varying,
    step_type character varying,
    status character varying,
    due_date timestamp with time zone,
    executed_at timestamp with time zone,
    urgency character varying,
    priority integer,
    sequence integer,
    rationale text,
    external_ticket_id character varying
);


ALTER TABLE public.workflow_steps OWNER TO pulse_ai_user;

--
-- Name: workflows; Type: TABLE; Schema: public; Owner: pulse_ai_user
--

CREATE TABLE public.workflows (
    id character varying NOT NULL,
    type character varying NOT NULL,
    employee_id character varying NOT NULL,
    status character varying,
    progress_percent integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.workflows OWNER TO pulse_ai_user;

--
-- Name: ai_configuration ai_configuration_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.ai_configuration
    ADD CONSTRAINT ai_configuration_pkey PRIMARY KEY (id);


--
-- Name: ai_observability_events ai_observability_events_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.ai_observability_events
    ADD CONSTRAINT ai_observability_events_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alert_recipient_states alert_recipient_states_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alert_recipient_states
    ADD CONSTRAINT alert_recipient_states_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: attendances attendances_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: base_templates base_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.base_templates
    ADD CONSTRAINT base_templates_pkey PRIMARY KEY (id);


--
-- Name: benefit_plans benefit_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.benefit_plans
    ADD CONSTRAINT benefit_plans_pkey PRIMARY KEY (id);


--
-- Name: career_paths career_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.career_paths
    ADD CONSTRAINT career_paths_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: data_access_policies data_access_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.data_access_policies
    ADD CONSTRAINT data_access_policies_pkey PRIMARY KEY (id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: document_access_events document_access_events_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_access_events
    ADD CONSTRAINT document_access_events_pkey PRIMARY KEY (id);


--
-- Name: document_templates document_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_templates
    ADD CONSTRAINT document_templates_pkey PRIMARY KEY (id);


--
-- Name: document_types document_types_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_types
    ADD CONSTRAINT document_types_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: employee_benefits employee_benefits_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_benefits
    ADD CONSTRAINT employee_benefits_pkey PRIMARY KEY (id);


--
-- Name: employee_skills employee_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: engagement_events engagement_events_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.engagement_events
    ADD CONSTRAINT engagement_events_pkey PRIMARY KEY (id);


--
-- Name: engagement_snapshots engagement_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.engagement_snapshots
    ADD CONSTRAINT engagement_snapshots_pkey PRIMARY KEY (id);


--
-- Name: generated_reports generated_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.generated_reports
    ADD CONSTRAINT generated_reports_pkey PRIMARY KEY (id);


--
-- Name: guardrails guardrails_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.guardrails
    ADD CONSTRAINT guardrails_pkey PRIMARY KEY (id);


--
-- Name: import_history import_history_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.import_history
    ADD CONSTRAINT import_history_pkey PRIMARY KEY (id);


--
-- Name: interviews interviews_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: leaves leaves_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT leaves_pkey PRIMARY KEY (id);


--
-- Name: mobility_requests mobility_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.mobility_requests
    ADD CONSTRAINT mobility_requests_pkey PRIMARY KEY (id);


--
-- Name: notification_configs notification_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.notification_configs
    ADD CONSTRAINT notification_configs_pkey PRIMARY KEY (id);


--
-- Name: performance_objectives performance_objectives_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_objectives
    ADD CONSTRAINT performance_objectives_pkey PRIMARY KEY (id);


--
-- Name: performance_reviews performance_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_pkey PRIMARY KEY (id);


--
-- Name: prediction_snapshots prediction_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.prediction_snapshots
    ADD CONSTRAINT prediction_snapshots_pkey PRIMARY KEY (id);


--
-- Name: project_assignments project_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.project_assignments
    ADD CONSTRAINT project_assignments_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: promotion_history promotion_history_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.promotion_history
    ADD CONSTRAINT promotion_history_pkey PRIMARY KEY (id);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: template_assets template_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.template_assets
    ADD CONSTRAINT template_assets_pkey PRIMARY KEY (id);


--
-- Name: training_courses training_courses_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.training_courses
    ADD CONSTRAINT training_courses_pkey PRIMARY KEY (id);


--
-- Name: training_enrollments training_enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.training_enrollments
    ADD CONSTRAINT training_enrollments_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: workflow_steps workflow_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_pkey PRIMARY KEY (id);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (id);


--
-- Name: ix_ai_observability_events_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_ai_observability_events_user_id ON public.ai_observability_events USING btree (user_id);


--
-- Name: ix_alert_recipient_states_alert_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_alert_recipient_states_alert_id ON public.alert_recipient_states USING btree (alert_id);


--
-- Name: ix_alert_recipient_states_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_alert_recipient_states_user_id ON public.alert_recipient_states USING btree (user_id);


--
-- Name: ix_alerts_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_alerts_employee_id ON public.alerts USING btree (employee_id);


--
-- Name: ix_alerts_fingerprint; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_alerts_fingerprint ON public.alerts USING btree (fingerprint);


--
-- Name: ix_alerts_target_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_alerts_target_user_id ON public.alerts USING btree (target_user_id);


--
-- Name: ix_alerts_workflow_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_alerts_workflow_id ON public.alerts USING btree (workflow_id);


--
-- Name: ix_career_paths_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_career_paths_employee_id ON public.career_paths USING btree (employee_id);


--
-- Name: ix_career_paths_target_job_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_career_paths_target_job_id ON public.career_paths USING btree (target_job_id);


--
-- Name: ix_chat_messages_conversation_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_chat_messages_conversation_id ON public.chat_messages USING btree (conversation_id);


--
-- Name: ix_conversations_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_conversations_user_id ON public.conversations USING btree (user_id);


--
-- Name: ix_data_access_policies_field_key; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_data_access_policies_field_key ON public.data_access_policies USING btree (field_key);


--
-- Name: ix_data_access_policies_resource; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_data_access_policies_resource ON public.data_access_policies USING btree (resource);


--
-- Name: ix_data_access_policies_role; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_data_access_policies_role ON public.data_access_policies USING btree (role);


--
-- Name: ix_data_access_policies_scope; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_data_access_policies_scope ON public.data_access_policies USING btree (scope);


--
-- Name: ix_departments_name; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_departments_name ON public.departments USING btree (name);


--
-- Name: ix_document_access_events_document_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_document_access_events_document_id ON public.document_access_events USING btree (document_id);


--
-- Name: ix_document_types_code; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_document_types_code ON public.document_types USING btree (code);


--
-- Name: ix_employee_benefits_benefit_plan_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_employee_benefits_benefit_plan_id ON public.employee_benefits USING btree (benefit_plan_id);


--
-- Name: ix_employee_benefits_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_employee_benefits_employee_id ON public.employee_benefits USING btree (employee_id);


--
-- Name: ix_employee_skills_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_employee_skills_employee_id ON public.employee_skills USING btree (employee_id);


--
-- Name: ix_employee_skills_skill_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_employee_skills_skill_id ON public.employee_skills USING btree (skill_id);


--
-- Name: ix_employees_email; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_employees_email ON public.employees USING btree (email);


--
-- Name: ix_employees_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_employees_user_id ON public.employees USING btree (user_id);


--
-- Name: ix_engagement_events_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_engagement_events_employee_id ON public.engagement_events USING btree (employee_id);


--
-- Name: ix_engagement_snapshots_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_engagement_snapshots_employee_id ON public.engagement_snapshots USING btree (employee_id);


--
-- Name: ix_interviews_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_interviews_employee_id ON public.interviews USING btree (employee_id);


--
-- Name: ix_interviews_manager_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_interviews_manager_id ON public.interviews USING btree (manager_id);


--
-- Name: ix_mobility_requests_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_mobility_requests_employee_id ON public.mobility_requests USING btree (employee_id);


--
-- Name: ix_mobility_requests_target_department_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_mobility_requests_target_department_id ON public.mobility_requests USING btree (target_department_id);


--
-- Name: ix_mobility_requests_target_job_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_mobility_requests_target_job_id ON public.mobility_requests USING btree (target_job_id);


--
-- Name: ix_notification_configs_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_notification_configs_user_id ON public.notification_configs USING btree (user_id);


--
-- Name: ix_performance_objectives_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_performance_objectives_employee_id ON public.performance_objectives USING btree (employee_id);


--
-- Name: ix_performance_objectives_owner_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_performance_objectives_owner_id ON public.performance_objectives USING btree (owner_id);


--
-- Name: ix_performance_reviews_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_performance_reviews_employee_id ON public.performance_reviews USING btree (employee_id);


--
-- Name: ix_performance_reviews_reviewer_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_performance_reviews_reviewer_id ON public.performance_reviews USING btree (reviewer_id);


--
-- Name: ix_prediction_snapshots_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_prediction_snapshots_employee_id ON public.prediction_snapshots USING btree (employee_id);


--
-- Name: ix_project_assignments_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_project_assignments_employee_id ON public.project_assignments USING btree (employee_id);


--
-- Name: ix_project_assignments_project_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_project_assignments_project_id ON public.project_assignments USING btree (project_id);


--
-- Name: ix_promotion_history_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_promotion_history_employee_id ON public.promotion_history USING btree (employee_id);


--
-- Name: ix_skills_name; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_skills_name ON public.skills USING btree (name);


--
-- Name: ix_template_assets_key; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_template_assets_key ON public.template_assets USING btree (key);


--
-- Name: ix_training_enrollments_employee_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_training_enrollments_employee_id ON public.training_enrollments USING btree (employee_id);


--
-- Name: ix_training_enrollments_training_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE INDEX ix_training_enrollments_training_id ON public.training_enrollments USING btree (training_id);


--
-- Name: ix_user_preferences_user_id; Type: INDEX; Schema: public; Owner: pulse_ai_user
--

CREATE UNIQUE INDEX ix_user_preferences_user_id ON public.user_preferences USING btree (user_id);


--
-- Name: alert_recipient_states alert_recipient_states_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alert_recipient_states
    ADD CONSTRAINT alert_recipient_states_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES public.alerts(id) ON DELETE CASCADE;


--
-- Name: alerts alerts_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: alerts alerts_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id);


--
-- Name: attendances attendances_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.attendances
    ADD CONSTRAINT attendances_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: career_paths career_paths_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.career_paths
    ADD CONSTRAINT career_paths_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: career_paths career_paths_target_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.career_paths
    ADD CONSTRAINT career_paths_target_job_id_fkey FOREIGN KEY (target_job_id) REFERENCES public.jobs(id);


--
-- Name: chat_messages chat_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: contracts contracts_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: document_access_events document_access_events_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_access_events
    ADD CONSTRAINT document_access_events_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- Name: document_templates document_templates_base_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_templates
    ADD CONSTRAINT document_templates_base_template_id_fkey FOREIGN KEY (base_template_id) REFERENCES public.base_templates(id);


--
-- Name: document_templates document_templates_document_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.document_templates
    ADD CONSTRAINT document_templates_document_type_id_fkey FOREIGN KEY (document_type_id) REFERENCES public.document_types(id);


--
-- Name: documents documents_document_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_document_type_id_fkey FOREIGN KEY (document_type_id) REFERENCES public.document_types(id);


--
-- Name: documents documents_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_benefits employee_benefits_benefit_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_benefits
    ADD CONSTRAINT employee_benefits_benefit_plan_id_fkey FOREIGN KEY (benefit_plan_id) REFERENCES public.benefit_plans(id);


--
-- Name: employee_benefits employee_benefits_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_benefits
    ADD CONSTRAINT employee_benefits_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_skills employee_skills_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employee_skills employee_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id);


--
-- Name: employees employees_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: employees employees_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: employees employees_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id);


--
-- Name: engagement_events engagement_events_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.engagement_events
    ADD CONSTRAINT engagement_events_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: engagement_snapshots engagement_snapshots_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.engagement_snapshots
    ADD CONSTRAINT engagement_snapshots_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: departments fk_department_manager; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_department_manager FOREIGN KEY (manager_id) REFERENCES public.employees(id);


--
-- Name: projects fk_projects_manager; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT fk_projects_manager FOREIGN KEY (manager_id) REFERENCES public.employees(id);


--
-- Name: interviews interviews_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: interviews interviews_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.employees(id);


--
-- Name: leaves leaves_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT leaves_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: mobility_requests mobility_requests_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.mobility_requests
    ADD CONSTRAINT mobility_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: mobility_requests mobility_requests_target_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.mobility_requests
    ADD CONSTRAINT mobility_requests_target_department_id_fkey FOREIGN KEY (target_department_id) REFERENCES public.departments(id);


--
-- Name: mobility_requests mobility_requests_target_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.mobility_requests
    ADD CONSTRAINT mobility_requests_target_job_id_fkey FOREIGN KEY (target_job_id) REFERENCES public.jobs(id);


--
-- Name: performance_objectives performance_objectives_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_objectives
    ADD CONSTRAINT performance_objectives_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: performance_objectives performance_objectives_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_objectives
    ADD CONSTRAINT performance_objectives_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.employees(id);


--
-- Name: performance_reviews performance_reviews_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: performance_reviews performance_reviews_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.employees(id);


--
-- Name: prediction_snapshots prediction_snapshots_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.prediction_snapshots
    ADD CONSTRAINT prediction_snapshots_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: project_assignments project_assignments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.project_assignments
    ADD CONSTRAINT project_assignments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: project_assignments project_assignments_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.project_assignments
    ADD CONSTRAINT project_assignments_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: promotion_history promotion_history_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.promotion_history
    ADD CONSTRAINT promotion_history_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: tasks tasks_assignee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES public.employees(id);


--
-- Name: tasks tasks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: training_courses training_courses_target_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.training_courses
    ADD CONSTRAINT training_courses_target_skill_id_fkey FOREIGN KEY (target_skill_id) REFERENCES public.skills(id);


--
-- Name: training_enrollments training_enrollments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.training_enrollments
    ADD CONSTRAINT training_enrollments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: training_enrollments training_enrollments_training_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.training_enrollments
    ADD CONSTRAINT training_enrollments_training_id_fkey FOREIGN KEY (training_id) REFERENCES public.training_courses(id);


--
-- Name: workflow_steps workflow_steps_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id);


--
-- Name: workflows workflows_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pulse_ai_user
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 70PEbyHXzNmFz1LBEJ06cr6BLAJQtCtWunkwC6nR3xD31O33fI4dy5GCHWvsafw

