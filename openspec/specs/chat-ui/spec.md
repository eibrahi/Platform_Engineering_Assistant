# chat-ui Specification                                                                                                                               
                                                                                                                                                    
## Purpose                                                                                                                                            
Eine Chat-Oberfläche mit Streamlit (ui/chat.py) für den Assistenten. Sie spricht nur über HTTP mit der API und kennt weder das Datenbank-Passwort noch
den OpenAI-Key.                                                                                                                                       
                                                                                                                                                    
## Requirements                                                                                                                                       
                                                                                                                                                    
### Requirement: Nur über die API                                                                                                                     
Die Oberfläche SHALL ausschließlich über HTTP mit der API unter /api/assistant sprechen und MUST NOT Code aus app/ importieren. Sie sendet bei jedem  
Aufruf den Header X-User-Id (vorerst fest Benutzer 1).                                                                                                
                                                                                                                                                    
#### Scenario: Backend läuft nicht                                                                                                                    
- **WHEN** die API nicht erreichbar ist                                                                                                               
- **THEN** zeigt die Oberfläche einen Fehler statt Daten                                                                                              
                                                                                                                                                    
### Requirement: Chatten                                                                                                                              
Die Oberfläche SHALL ein Eingabefeld bieten, die Frage sofort anzeigen, während des Wartens einen Hinweis zeigen und danach die Antwort des           
Assistenten anzeigen. Der Verlauf der aktuellen Unterhaltung MUST bei jeder Aktion erhalten bleiben.                                                  
                                                                                                                                                    
#### Scenario: Frage stellen                                                                                                                          
- **WHEN** ein Benutzer eine Frage abschickt                                                                                                          
- **THEN** erscheinen Frage und Antwort untereinander im Chat                                                                                         
                                                                                                                                                    
### Requirement: Unterhaltungen in der Seitenleiste                                                                                                   
Die Oberfläche SHALL in der Seitenleiste alle eigenen Unterhaltungen als Buttons mit Nummer und Uhrzeit in lokaler Zeit (TT.MM. HH:MM) zeigen, die    
neueste oben, und die aktuelle hervorheben.                                                                                                           
                                                                                                                                                    
#### Scenario: Neue Unterhaltung erscheint sofort                                                                                                     
- **WHEN** ein Benutzer die erste Nachricht einer neuen Unterhaltung abschickt                                                                        
- **THEN** erscheint die Unterhaltung nach der Antwort sofort in der Seitenleiste und ist hervorgehoben

### Requirement: Unterhaltung öffnen                                                                                                                  
Die Oberfläche SHALL beim Klick auf eine Unterhaltung ihren Verlauf aus der API laden und anzeigen, sodass der Benutzer dort weiterschreiben kann.    
                                                                                                                                                    
#### Scenario: Alte Unterhaltung fortsetzen                                                                                                           
- **WHEN** ein Benutzer auf eine ältere Unterhaltung klickt und eine Frage stellt                                                                     
- **THEN** wird ihr Verlauf angezeigt und die Frage in dieser Unterhaltung beantwortet                                                                
                                                                                                                                                    
### Requirement: Neue Unterhaltung starten                                                                                                            
Die Oberfläche SHALL einen Button "Neue Unterhaltung" bieten, der den Chat leert. Die nächste Nachricht MUST eine neue Unterhaltung anlegen.          
                                                                                                                                                    
#### Scenario: Neu anfangen                                                                                                                           
- **WHEN** ein Benutzer auf "Neue Unterhaltung" klickt                                                                                                
- **THEN** ist der Chat leer, und die nächste Frage legt eine neue Unterhaltung an                                                                    
                                                                                                                                                    
### Requirement: Verhalten nach Neuladen                                                                                                              
Nach einem Neuladen der Seite (F5) SHALL die Oberfläche leer starten. Alle Unterhaltungen MUST über die Seitenleiste weiter erreichbar sein.          
                                                                                                                                                    
#### Scenario: F5 drücken                                                                                                                             
- **WHEN** ein Benutzer die Seite neu lädt                                                                                                            
- **THEN** ist der Chat leer, und die bisherigen Unterhaltungen stehen in der Seitenleiste
