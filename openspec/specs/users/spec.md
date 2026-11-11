# users Specification                                                                                                                                 
                                                                                                                                                
## Purpose                                                                                                                                            
Benutzer über die REST-API unter /api/users verwalten. Benutzer werden nicht gelöscht, sondern deaktiviert, weil Deployments und Unterhaltungen auf   
sie verweisen.                                                                                                                                        
                                                                                                                                                
## Requirements                                                                                                                                       
                                                                                                                                                
### Requirement: Benutzer anlegen                                                                                                                     
Das System SHALL über POST /api/users einen Benutzer mit name und gültiger email anlegen und mit 201 antworten. Ohne Angabe gilt role = viewer.       
Erlaubte Rollen sind admin, platform_engineer und viewer.                                                                                             
                                                                                                                                                
#### Scenario: Benutzer ohne Rolle                                                                                                                    
- **WHEN** ein Client nur name und email sendet                                                                                                       
- **THEN** antwortet die API mit 201, role = viewer und is_active = true                                                                              
                                                                                                                                                
#### Scenario: Ungültige E-Mail                                                                                                                       
- **WHEN** ein Client email = keine-mail sendet                                                                                                       
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                                
### Requirement: Eindeutige E-Mail                                                                                                                    
Das System MUST doppelte E-Mail-Adressen beim Anlegen und Ändern ablehnen.                                                                            
                                                                                                                                                
#### Scenario: E-Mail bereits vergeben                                                                                                                
- **WHEN** ein Client einen Benutzer mit einer schon vorhandenen E-Mail anlegt                                                                        
- **THEN** antwortet die API mit 409 und der Meldung "Ein User mit dieser E-Mail-Adresse existiert bereits"                                           
                                                                                                                                                
### Requirement: Benutzer auflisten                                                                                                                   
Das System SHALL über GET /api/users die Benutzer nach id aufsteigend liefern, standardmäßig nur aktive. Mit include_inactive=true kommen auch        
deaktivierte dazu, und role filtert nach Rolle.

#### Scenario: Deaktivierte sind standardmäßig ausgeblendet                                                                                           
- **WHEN** ein Client GET /api/users ohne Parameter aufruft                                                                                           
- **THEN** enthält die Antwort keine deaktivierten Benutzer                                                                                           
                                                                                                                                                
#### Scenario: Deaktivierte einblenden                                                                                                                
- **WHEN** ein Client GET /api/users?include_inactive=true aufruft                                                                                    
- **THEN** enthält die Antwort auch deaktivierte Benutzer                                                                                             
                                                                                                                                                
### Requirement: Benutzer lesen und ändern                                                                                                            
Das System SHALL über GET und PUT /api/users/{id} einen Benutzer liefern beziehungsweise nur die mitgeschickten Felder ändern. Unbekannte ids MUST mit
404 beantwortet werden.                                                                                                                               
                                                                                                                                                
#### Scenario: Unbekannter Benutzer                                                                                                                   
- **WHEN** ein Client eine nicht vorhandene id abruft                                                                                                 
- **THEN** antwortet die API mit 404 und der Meldung "User nicht gefunden"                                                                            
                                                                                                                                                
### Requirement: Benutzer deaktivieren statt löschen                                                                                                  
Das System SHALL bei DELETE /api/users/{id} den Benutzer nur deaktivieren (is_active = false) und mit 204 antworten. Die Zeile MUST erhalten bleiben. 
                                                                                                                                                
#### Scenario: Benutzer deaktivieren                                                                                                                  
- **WHEN** ein Client DELETE /api/users/{id} aufruft                                                                                                  
- **THEN** antwortet die API mit 204, und der Benutzer existiert weiter mit is_active = false
