# conversation-history Specification                                                                                                                  
                                                                                                                                                    
## Purpose                                                                                                                                            
Benutzer können ihre bisherigen Unterhaltungen mit dem Assistenten auflisten und den Verlauf einer Unterhaltung lesen. Fremde Unterhaltungen bleiben  
unsichtbar.                                                                                                                                           
                                                                                                                                                    
## Requirements                                                                                                                                       
                                                                                                                                                    
### Requirement: Eigene Unterhaltungen auflisten                                                                                                      
Das System SHALL über GET /api/assistant/conversations nur die Unterhaltungen des anfragenden Benutzers liefern (id, platform_id, created_at), die    
neueste zuerst.                                                                                                                                       
                                                                                                                                                    
#### Scenario: Benutzer hat zwei Unterhaltungen                                                                                                       
- **WHEN** Benutzer 1 die Liste abruft                                                                                                                
- **THEN** erhält er genau seine zwei Unterhaltungen, die neueste zuerst                                                                              
                                                                                                                                                    
#### Scenario: Unterhaltungen anderer Benutzer                                                                                                        
- **WHEN** Benutzer 2 die Liste abruft                                                                                                                
- **THEN** enthält sie keine Unterhaltung von Benutzer 1                                                                                              
                                                                                                                                                    
### Requirement: Verlauf einer Unterhaltung lesen                                                                                                     
Das System SHALL über GET /api/assistant/conversations/{id}/messages die Nachrichten einer eigenen Unterhaltung liefern (id, role, content,           
created_at), die älteste zuerst.                                                                                                                      
                                                                                                                                                    
#### Scenario: Verlauf in Reihenfolge                                                                                                                 
- **WHEN** ein Benutzer den Verlauf einer Unterhaltung mit zwei Austauschen abruft                                                                    
- **THEN** erhält er vier Nachrichten in der Reihenfolge user, assistant, user, assistant                                                             
                                                                                                                                                    
### Requirement: Fremde Unterhaltungen sind unsichtbar                                                                                                
Das System MUST mit 404 antworten, wenn jemand den Verlauf einer fremden oder unbekannten Unterhaltung abruft.                                        
                                                                                                                                                    
#### Scenario: Zugriff auf fremde Unterhaltung                                                                                                        
- **WHEN** Benutzer 2 die Nachrichten einer Unterhaltung von Benutzer 1 abruft                                                                        
- **THEN** antwortet die API mit 404

### Requirement: Nur bekannte Benutzer
Das System MUST auch hier unbekannte oder deaktivierte Benutzer (Header X-User-Id) mit 403 abweisen.

#### Scenario: Deaktivierter Benutzer
- **WHEN** ein deaktivierter Benutzer seine Unterhaltungen abruft
- **THEN** antwortet die API mit 403
