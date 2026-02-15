# Append methods to ForumTaskManager
    def get_mission_steps(self, mission_id: int) -> List[Dict]:
        """Busca steps da missão"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM steps WHERE mission_id = ? ORDER BY step_number
        """, (mission_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def complete_step(self, step_id: int, output: str = None):
        """Marca step como completado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE steps 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, output_data = ?
            WHERE id = ?
        """, (json.dumps({'output': output}) if output else None, step_id))
        conn.commit()
        conn.close()
        logger.info(f"✅ Step {step_id} completado")
    
    def complete_mission(self, mission_id: int, result: str = None):
        """Marca missão como completada"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE missions 
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP, result = ?
            WHERE id = ?
        """, (json.dumps({'result': result}) if result else None, mission_id))
        conn.commit()
        conn.close()
        logger.info(f"✅ Missão {mission_id} completada")
    
    def complete_task(self, task_id: int, result: str = None):
        """Marca task como completada"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE forum_tasks 
            SET status = 'completed'
            WHERE id = ?
        """, (task_id,))
        conn.commit()
        conn.close()
        logger.info(f"✅ Task {task_id} completada")
