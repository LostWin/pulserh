<!DOCTYPE html>
<html class="${properties.kcHtmlClass!}" lang="fr">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Pulse AI · Modification du mot de passe</title>
    <link rel="icon" href="${url.resourcesPath}/img/favicon.png" />
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
                        <span>🔐</span>
                    </div>
                    <h2>Modification du mot de passe</h2>
                    <p>Veuillez définir un nouveau mot de passe pour votre compte.</p>
                </div>

                <#if message?has_content>
                    <div class="pulse-alert pulse-alert-${message.type!'info'}">
                        ${kcSanitize(message.summary)?no_esc}
                    </div>
                </#if>

                <form id="kc-passwd-update-form" class="pulse-login-form" action="${url.loginAction}" method="post">
                    <div class="pulse-field">
                        <label for="password-new">${msg("passwordNew")}</label>
                        <input
                            id="password-new"
                            name="password-new"
                            type="password"
                            autocomplete="new-password"
                            autofocus
                        />
                    </div>

                    <div class="pulse-field">
                        <label for="password-confirm">${msg("passwordConfirm")}</label>
                        <input
                            id="password-confirm"
                            name="password-confirm"
                            type="password"
                            autocomplete="new-password"
                        />
                    </div>

                    <#if isAppInitiatedAction??>
                        <div class="pulse-checkbox" style="margin-top: 1rem; margin-bottom: 1rem;">
                            <label>
                                <input type="checkbox" id="logout-sessions" name="logout-sessions" value="on" checked="checked">
                                <span>${msg("logoutOtherSessions")}</span>
                            </label>
                        </div>
                    </#if>

                    <button class="pulse-login-button" name="login" id="kc-login" type="submit">
                        Mettre à jour le mot de passe
                    </button>
                    
                    <#if isAppInitiatedAction??>
                        <div class="pulse-login-help" style="margin-top: 1rem;">
                            <button type="submit" name="cancel-aia" value="true" class="pulse-login-button pulse-login-button-secondary" style="background: transparent; color: var(--text-brand-secondary); border: 1px solid var(--border-color);">
                                ${msg("doCancel")}
                            </button>
                        </div>
                    </#if>
                </form>
            </section>
        </div>
    </div>
</body>
</html>
