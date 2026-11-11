# assistant-chat Specification                                                                                                                        
                                                                                                                                                    
## Purpose                                                                                                                                            
Über POST /api/assistant/chat mit dem Platform-Engineering-Assistenten (LangGraph und OpenAI) sprechen. Der Assistent erinnert sich an den Verlauf    
einer Unterhaltung, auch nach einem Neustart des Servers.                                                                                             
                                                                                                                                                    
## Requirements                                                                                                                                       
                                                                                                                                                    
### Requirement: Benutzer per Header erkennen                                                                                                         
Das System SHALL den Benutzer über den Header X-User-Id bestimmen. Unbekannte oder deaktivierte Benutzer MUST mit 403 abgewiesen werden. Das ist eine 
Übergangslösung bis zu einem echten Login.                                                                                                            
                                                                                                                                                    
#### Scenario: Unbekannter Benutzer                                                                                                                   
- **WHEN** ein Client X-User-Id = 999 sendet und es diesen Benutzer nicht gibt                                                                        
- **THEN** antwortet die API mit 403 und der Meldung "Unbekannter oder deaktivierter User"                                                            
                                                                                                                                                    
#### Scenario: Header fehlt                                                                                                                           
- **WHEN** ein Client keinen Header X-User-Id sendet                                                                                                  
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                                    
### Requirement: Nachricht prüfen                                                                                                                     
Das System MUST nur Nachrichten mit 1 bis 4000 Zeichen annehmen.                                                                                      
                                                                                                                                                    
#### Scenario: Leere Nachricht                                                                                                                        
- **WHEN** ein Client message = "" sendet                                                                                                             
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                                    
### Requirement: Neue Unterhaltung starten                                                                                                            
Das System SHALL eine neue Unterhaltung für den Benutzer anlegen, wenn conversation_id fehlt oder null ist, und ihre id in der Antwort zurückgeben.   
                                                                                                                                                    
#### Scenario: Erste Nachricht                                                                                                                        
- **WHEN** ein Benutzer ohne conversation_id fragt                                                                                                    
- **THEN** antwortet die API mit 200, einer neuen conversation_id und der Antwort des Assistenten

### Requirement: Unterhaltung fortsetzen                                                                                                              
Das System SHALL bei einer conversation_id die Unterhaltung des Benutzers fortsetzen. Fremde oder unbekannte Unterhaltungen MUST mit 404 beantwortet  
werden, damit niemand erfährt, ob es sie gibt.                                                                                                        
                                                                                                                                                    
#### Scenario: Fremde Unterhaltung                                                                                                                    
- **WHEN** Benutzer 2 eine conversation_id von Benutzer 1 sendet                                                                                      
- **THEN** antwortet die API mit 404 und der Meldung "Unterhaltung nicht gefunden"                                                                    
                                                                                                                                                    
### Requirement: Gedächtnis pro Unterhaltung                                                                                                          
Das System SHALL den Zustand des Graphen pro Unterhaltung in Postgres speichern (PostgresSaver mit thread_id = conversation_id). So kennt der         
Assistent frühere Nachrichten derselben Unterhaltung, auch nach einem Neustart des Servers. Verschiedene Unterhaltungen MUST NOT ihr Gedächtnis       
teilen.                                                                                                                                               
                                                                                                                                                    
#### Scenario: Assistent erinnert sich                                                                                                                
- **WHEN** ein Benutzer in Nachricht 1 seinen Namen nennt und in Nachricht 2 derselben Unterhaltung danach fragt                                      
- **THEN** nennt der Assistent den Namen                                                                                                              
                                                                                                                                                    
#### Scenario: Getrennte Unterhaltungen                                                                                                               
- **WHEN** ein Benutzer in einer neuen Unterhaltung nach dem Namen fragt                                                                              
- **THEN** kennt der Assistent ihn nicht                                                                                                              
                                                                                                                                                    
### Requirement: Lesbaren Verlauf speichern                                                                                                           
Das System SHALL Frage und Antwort als zwei Zeilen in messages speichern (role = user und role = assistant). Schlägt der Aufruf des Modells fehl, MUST
nichts gespeichert werden.                                                                                                                            
                                                                                                                                                    
#### Scenario: Erfolgreicher Austausch                                                                                                                
- **WHEN** der Assistent eine Frage beantwortet                                                                                                       
- **THEN** enthält messages für diese Unterhaltung genau eine neue Zeile mit role = user und eine mit role = assistant                                
                                                                                                                                                    
### Requirement: Verhalten des Assistenten                                                                                                            
Der Assistent SHALL als Platform-Engineering-Assistent für Cloud, Azure, Databricks, Deployments und IT-Infrastruktur auftreten, auf Deutsch kurz und 
präzise antworten und ehrlich sagen, wenn er etwas nicht weiß. Das Modell ist gpt-4.1-mini mit temperature = 0.

#### Scenario: Frage auf Deutsch                                                                                                                      
- **WHEN** ein Benutzer eine Fachfrage stellt                                                                                                         
- **THEN** antwortet der Assistent auf Deutsch
