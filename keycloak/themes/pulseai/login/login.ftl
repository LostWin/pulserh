<!DOCTYPE html>
<html class="${properties.kcHtmlClass!}" lang="fr">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Pulse AI · Connexion sécurisée</title>
    <link rel="icon" href="${url.resourcesPath}/img/pulse-logo.png?v=20260614c" />
    <link href="${url.resourcesPath}/css/login.css?v=20260614c" rel="stylesheet" />
</head>
<body class="pulse-login-body">
    <div class="pulse-login-shell">
        <div class="pulse-login-glow pulse-login-glow-left"></div>
        <div class="pulse-login-glow pulse-login-glow-right"></div>

        <div class="pulse-login-grid">
            <section class="pulse-brand-panel">
                <div class="pulse-brand-lockup">
                    <img src="${url.resourcesPath}/img/pulse-logo.png?v=20260614c" alt="Pulse AI" class="pulse-brand-logo" />
                    <div>
                        <h1 class="pulse-brand-title">Pulse AI</h1>
                        <p class="pulse-brand-subtitle">Enterprise Portal</p>
                    </div>
                </div>
                <p class="pulse-brand-copy">
                    La solution IA de nouvelle génération pour anticiper le désengagement et optimiser le pilotage de vos ressources humaines.
                </p>
            </section>

            <section class="pulse-login-card">
                <div class="pulse-login-card-header">
                    <div class="pulse-shield-badge">
                        <span>🛡️</span>
                    </div>
                    <h2>Authentification sécurisée</h2>
                    <p>Veuillez vous connecter avec votre compte d'entreprise.</p>
                </div>

                <#if message?has_content>
                    <div class="pulse-alert pulse-alert-${message.type!'info'}">
                        ${kcSanitize(message.summary)?no_esc}
                    </div>
                </#if>

                <form id="kc-form-login" class="pulse-login-form" action="${url.loginAction}" method="post">
                    <#if !usernameHidden??>
                        <div class="pulse-field">
                            <label for="username">
                                <#if !realm.loginWithEmailAllowed>${msg("username")}
                                <#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}
                                <#else>${msg("email")}</#if>
                            </label>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                value="${(login.username!'')}"
                                autocomplete="username"
                                autofocus
                            />
                        </div>
                    </#if>

                    <div class="pulse-field">
                        <label for="password">${msg("password")}</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            autocomplete="current-password"
                        />
                    </div>

                    <#if realm.rememberMe && !usernameHidden??>
                        <label class="pulse-checkbox">
                            <input id="rememberMe" name="rememberMe" type="checkbox" <#if login.rememberMe??>checked</#if>>
                            <span>${msg("rememberMe")}</span>
                        </label>
                    </#if>

                    <button class="pulse-login-button" name="login" id="kc-login" type="submit">
                        Se connecter avec Keycloak
                    </button>

                    <#if realm.resetPasswordAllowed>
                        <div class="pulse-login-help">
                            <a href="${url.loginResetCredentialsUrl}">${msg("doForgotPassword")}</a>
                        </div>
                    </#if>
                </form>
            </section>
        </div>
    </div>
</body>
</html>
