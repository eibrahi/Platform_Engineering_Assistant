# incidents Specification                                                                                                                             
                                                                                                                                                    
## Purpose                                                                                                                                            
Incidents zu einer Plattform über die REST-API unter /api/incidents erfassen, auflisten und bearbeiten. Später erkennt der Assistent Incidents selbst 
und schlägt Lösungen vor.                                                                                                                             
                                                                                                                                                    
## Requirements                                                                                                                                       
                                                                                                                                                    
### Requirement: Incident anlegen                                                                                                                     
Das System SHALL über POST /api/incidents einen Incident zu einer vorhandenen Plattform anlegen und mit 201 antworten. Der Status MUST beim Anlegen   
immer open sein. Ohne Angabe gilt severity = medium. Erlaubte Werte für severity sind low, medium, high und critical.                                 
                                                                                                                                                    
#### Scenario: Gültiger Incident                                                                                                                      
- **WHEN** ein Client platform_id und title sendet                                                                                                    
- **THEN** antwortet die API mit 201, status = open, severity = medium und resolved_at = null                                                         
                                                                                                                                                    
#### Scenario: Unbekannte Plattform                                                                                                                   
- **WHEN** ein Client eine platform_id sendet, die es nicht gibt                                                                                      
- **THEN** antwortet die API mit 422 und der Meldung "Plattform <id> existiert nicht"                                                                 
                                                                                                                                                    
### Requirement: Incidents auflisten und filtern                                                                                                      
Das System SHALL über GET /api/incidents die Incidents liefern, die neuesten zuerst. Die Liste MUST optional nach platform_id, status und severity    
gefiltert werden können.                                                                                                                              
                                                                                                                                                    
#### Scenario: Offene Incidents einer Plattform                                                                                                       
- **WHEN** ein Client GET /api/incidents?platform_id=1&status=open aufruft                                                                            
- **THEN** enthält die Antwort nur offene Incidents von Plattform 1, die neuesten zuerst                                                              
                                                                                                                                                    
### Requirement: Einzelnen Incident lesen                                                                                                             
Das System SHALL über GET /api/incidents/{id} einen Incident liefern und mit 404 antworten, wenn es ihn nicht gibt.                                   
                                                                                                                                                    
#### Scenario: Unbekannter Incident                                                                                                                   
- **WHEN** ein Client eine nicht vorhandene id abruft                                                                                                 
- **THEN** antwortet die API mit 404 und der Meldung "Incident nicht gefunden"

### Requirement: Incident bearbeiten                                                                                                                  
Das System SHALL über PUT /api/incidents/{id} nur die mitgeschickten Felder title, description, severity, status und root_cause ändern. platform_id   
und resolved_at MUST NOT direkt änderbar sein. title, severity und status MUST NOT auf null gesetzt werden.                                           
                                                                                                                                                    
#### Scenario: Pflichtfeld auf null                                                                                                                   
- **WHEN** ein Client title = null sendet                                                                                                             
- **THEN** antwortet die API mit 422                                                                                                                  
                                                                                                                                                    
### Requirement: resolved_at folgt dem Status                                                                                                         
Das System SHALL resolved_at automatisch setzen, wenn der Status auf resolved wechselt, und es wieder leeren, wenn der Status von resolved weg        
wechselt.                                                                                                                                             
                                                                                                                                                    
#### Scenario: Incident wird gelöst                                                                                                                   
- **WHEN** ein Client bei einem offenen Incident status = resolved sendet                                                                             
- **THEN** ist resolved_at gesetzt                                                                                                                    
                                                                                                                                                    
#### Scenario: Incident wird wieder geöffnet                                                                                                          
- **WHEN** ein Client bei einem gelösten Incident status = investigating sendet                                                                       
- **THEN** ist resolved_at wieder null
