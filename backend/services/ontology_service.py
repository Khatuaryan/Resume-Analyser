"""
Knowledge Graph and Ontology Integration Service
Builds and integrates skill/job ontology for deeper semantic matching
to enhance candidate-job scoring and skill recommendations.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import networkx as nx
import json
from datetime import datetime
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class OntologyService:
    """Service for knowledge graph and ontology integration."""
    
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()
        self.skill_ontology = {}
        self.job_ontology = {}
        self.skill_relationships = {}
        self.job_skill_mappings = {}
        self.initialized = False
        
        # Initialize with basic ontology
        self._initialize_basic_ontology()
    
    def _initialize_basic_ontology(self):
        """Initialize basic skill and job ontology."""
        # Skill categories and relationships
        self.skill_ontology = {
            'programming_languages': {
                'python': {'level': 'intermediate', 'category': 'backend', 'related': ['django', 'flask', 'pandas', 'numpy']},
                'javascript': {'level': 'intermediate', 'category': 'frontend', 'related': ['react', 'node', 'vue', 'angular']},
                'java': {'level': 'intermediate', 'category': 'backend', 'related': ['spring', 'hibernate', 'maven']},
                'sql': {'level': 'beginner', 'category': 'database', 'related': ['mysql', 'postgresql', 'oracle']},
                'go': {'level': 'advanced', 'category': 'backend', 'related': ['kubernetes', 'docker', 'microservices']},
                'rust': {'level': 'advanced', 'category': 'systems', 'related': ['cargo', 'tokio', 'actix']}
            },
            'frameworks': {
                'react': {'level': 'intermediate', 'category': 'frontend', 'related': ['javascript', 'redux', 'jsx']},
                'django': {'level': 'intermediate', 'category': 'backend', 'related': ['python', 'orm', 'mvc']},
                'spring': {'level': 'intermediate', 'category': 'backend', 'related': ['java', 'hibernate', 'mvc']},
                'express': {'level': 'intermediate', 'category': 'backend', 'related': ['javascript', 'node', 'middleware']},
                'flask': {'level': 'beginner', 'category': 'backend', 'related': ['python', 'jinja2', 'werkzeug']}
            },
            'databases': {
                'mysql': {'level': 'intermediate', 'category': 'database', 'related': ['sql', 'innodb', 'replication']},
                'postgresql': {'level': 'intermediate', 'category': 'database', 'related': ['sql', 'json', 'indexing']},
                'mongodb': {'level': 'intermediate', 'category': 'nosql', 'related': ['document', 'aggregation', 'sharding']},
                'redis': {'level': 'intermediate', 'category': 'cache', 'related': ['memory', 'pubsub', 'clustering']}
            },
            'cloud_platforms': {
                'aws': {'level': 'intermediate', 'category': 'cloud', 'related': ['ec2', 's3', 'lambda', 'rds']},
                'azure': {'level': 'intermediate', 'category': 'cloud', 'related': ['vm', 'storage', 'functions', 'sql']},
                'gcp': {'level': 'intermediate', 'category': 'cloud', 'related': ['compute', 'storage', 'functions', 'bigquery']},
                'docker': {'level': 'intermediate', 'category': 'containerization', 'related': ['kubernetes', 'containers', 'images']},
                'kubernetes': {'level': 'advanced', 'category': 'orchestration', 'related': ['docker', 'pods', 'services', 'deployments']}
            },
            'tools': {
                'git': {'level': 'beginner', 'category': 'version_control', 'related': ['github', 'gitlab', 'branching']},
                'jenkins': {'level': 'intermediate', 'category': 'ci_cd', 'related': ['pipeline', 'automation', 'deployment']},
                'terraform': {'level': 'advanced', 'category': 'infrastructure', 'related': ['iac', 'aws', 'azure', 'gcp']}
            }
        }
        
        # Job role ontology
        self.job_ontology = {
            'software_engineer': {
                'required_skills': ['programming', 'algorithms', 'data_structures'],
                'preferred_skills': ['testing', 'debugging', 'code_review'],
                'experience_level': 'mid',
                'related_roles': ['backend_engineer', 'frontend_engineer', 'fullstack_engineer']
            },
            'data_scientist': {
                'required_skills': ['python', 'statistics', 'machine_learning'],
                'preferred_skills': ['pandas', 'scikit-learn', 'tensorflow'],
                'experience_level': 'mid',
                'related_roles': ['data_analyst', 'ml_engineer', 'research_scientist']
            },
            'devops_engineer': {
                'required_skills': ['docker', 'kubernetes', 'aws'],
                'preferred_skills': ['terraform', 'jenkins', 'monitoring'],
                'experience_level': 'mid',
                'related_roles': ['sre', 'cloud_engineer', 'platform_engineer']
            },
            'frontend_developer': {
                'required_skills': ['javascript', 'html', 'css'],
                'preferred_skills': ['react', 'vue', 'angular'],
                'experience_level': 'junior',
                'related_roles': ['ui_developer', 'ux_developer', 'web_developer']
            }
        }
        
        # Build knowledge graph
        self._build_knowledge_graph()
    
    def _build_knowledge_graph(self):
        """Build knowledge graph from ontology."""
        # Add skill nodes
        for category, skills in self.skill_ontology.items():
            for skill, attributes in skills.items():
                # Create a copy of attributes to avoid conflicts
                node_attributes = attributes.copy()
                node_attributes.update({
                    'type': 'skill',
                    'category': category,
                    'level': attributes.get('level', 'beginner')
                })
                self.knowledge_graph.add_node(skill, **node_attributes)
        
        # Add job nodes
        for job, attributes in self.job_ontology.items():
            self.knowledge_graph.add_node(
                job,
                type='job',
                **attributes
            )
        
        # Add relationships
        for category, skills in self.skill_ontology.items():
            for skill, attributes in skills.items():
                # Add related skills
                for related_skill in attributes.get('related', []):
                    if related_skill in self.knowledge_graph:
                        self.knowledge_graph.add_edge(skill, related_skill, relationship='related')
                
                # Add category relationships
                self.knowledge_graph.add_edge(skill, category, relationship='belongs_to')
        
        # Add job-skill relationships
        for job, attributes in self.job_ontology.items():
            for skill in attributes.get('required_skills', []):
                if skill in self.knowledge_graph:
                    self.knowledge_graph.add_edge(job, skill, relationship='requires')
            
            for skill in attributes.get('preferred_skills', []):
                if skill in self.knowledge_graph:
                    self.knowledge_graph.add_edge(job, skill, relationship='prefers')
    
    async def initialize(self):
        """Initialize ontology service."""
        if self.initialized:
            return
        
        try:
            # Load additional ontology data if available
            await self._load_ontology_data()
            
            self.initialized = True
            logger.info("Ontology service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing ontology service: {e}")
            self.initialized = False
    
    async def _load_ontology_data(self):
        """Load additional ontology data from files."""
        ontology_file = Path("data/ontology.json")
        if ontology_file.exists():
            try:
                with open(ontology_file, 'r') as f:
                    additional_data = json.load(f)
                
                # Merge additional data
                if 'skills' in additional_data:
                    self.skill_ontology.update(additional_data['skills'])
                
                if 'jobs' in additional_data:
                    self.job_ontology.update(additional_data['jobs'])
                
                # Rebuild knowledge graph
                self._build_knowledge_graph()
                
            except Exception as e:
                logger.warning(f"Could not load additional ontology data: {e}")
    
    async def find_related_skills(self, skill: str, max_depth: int = 2) -> List[str]:
        """Find related skills in the knowledge graph."""
        if skill not in self.knowledge_graph:
            return []
        
        related_skills = set()
        
        # Find skills within max_depth
        for depth in range(1, max_depth + 1):
            for node in nx.single_source_shortest_path_length(self.knowledge_graph, skill, cutoff=depth):
                if (node != skill and 
                    self.knowledge_graph.nodes[node].get('type') == 'skill'):
                    related_skills.add(node)
        
        return list(related_skills)
    
    async def calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills."""
        if skill1 == skill2:
            return 1.0
        
        if skill1 not in self.knowledge_graph or skill2 not in self.knowledge_graph:
            return 0.0
        
        try:
            # Calculate shortest path
            path_length = nx.shortest_path_length(self.knowledge_graph, skill1, skill2)
            
            # Convert path length to similarity (shorter path = higher similarity)
            similarity = 1.0 / (1.0 + path_length)
            
            return similarity
            
        except nx.NetworkXNoPath:
            return 0.0
    
    async def enhance_candidate_scoring(
        self, 
        candidate_skills: List[str], 
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance candidate scoring using ontology."""
        required_skills = job_requirements.get('required_skills', [])
        preferred_skills = job_requirements.get('preferred_skills', [])
        
        # Calculate semantic matches
        semantic_matches = await self._find_semantic_matches(candidate_skills, required_skills)
        preferred_matches = await self._find_semantic_matches(candidate_skills, preferred_skills)
        
        # Calculate skill gaps
        skill_gaps = await self._identify_skill_gaps(candidate_skills, required_skills)
        
        # Calculate learning recommendations
        learning_recommendations = await self._generate_learning_recommendations(
            candidate_skills, required_skills, preferred_skills
        )
        
        # Calculate ontology-enhanced score
        base_score = len(semantic_matches) / max(len(required_skills), 1) * 100
        preferred_bonus = len(preferred_matches) * 5
        ontology_score = min(100, base_score + preferred_bonus)
        
        return {
            'ontology_score': round(ontology_score, 2),
            'semantic_matches': semantic_matches,
            'preferred_matches': preferred_matches,
            'skill_gaps': skill_gaps,
            'learning_recommendations': learning_recommendations,
            'confidence': self._calculate_ontology_confidence(semantic_matches, required_skills)
        }
    
    async def _find_semantic_matches(self, candidate_skills: List[str], target_skills: List[str]) -> List[Dict[str, Any]]:
        """Find semantic matches between candidate and target skills."""
        matches = []
        
        for target_skill in target_skills:
            best_match = None
            best_similarity = 0.0
            
            for candidate_skill in candidate_skills:
                # Direct match
                if candidate_skill.lower() == target_skill.lower():
                    best_match = {
                        'candidate_skill': candidate_skill,
                        'target_skill': target_skill,
                        'similarity': 1.0,
                        'match_type': 'exact'
                    }
                    best_similarity = 1.0
                    break
                
                # Semantic match
                similarity = await self.calculate_skill_similarity(candidate_skill, target_skill)
                if similarity > best_similarity and similarity > 0.3:  # Threshold for semantic match
                    best_match = {
                        'candidate_skill': candidate_skill,
                        'target_skill': target_skill,
                        'similarity': similarity,
                        'match_type': 'semantic'
                    }
                    best_similarity = similarity
            
            if best_match:
                matches.append(best_match)
        
        return matches
    
    async def _identify_skill_gaps(self, candidate_skills: List[str], required_skills: List[str]) -> List[Dict[str, Any]]:
        """Identify skill gaps and suggest alternatives."""
        gaps = []
        
        for required_skill in required_skills:
            # Check for direct match
            if any(candidate_skill.lower() == required_skill.lower() for candidate_skill in candidate_skills):
                continue
            
            # Check for semantic match
            has_semantic_match = False
            for candidate_skill in candidate_skills:
                similarity = await self.calculate_skill_similarity(candidate_skill, required_skill)
                if similarity > 0.3:
                    has_semantic_match = True
                    break
            
            if not has_semantic_match:
                # Find related skills that might help
                related_skills = await self.find_related_skills(required_skill)
                candidate_related = [skill for skill in candidate_skills if skill in related_skills]
                
                gaps.append({
                    'missing_skill': required_skill,
                    'related_candidate_skills': candidate_related,
                    'learning_path': related_skills[:3]  # Top 3 related skills to learn
                })
        
        return gaps
    
    async def _generate_learning_recommendations(
        self, 
        candidate_skills: List[str], 
        required_skills: List[str], 
        preferred_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate learning recommendations based on ontology."""
        recommendations = []
        
        # Find missing skills
        missing_skills = []
        for skill in required_skills + preferred_skills:
            if not any(candidate_skill.lower() == skill.lower() for candidate_skill in candidate_skills):
                missing_skills.append(skill)
        
        for missing_skill in missing_skills:
            # Find related skills to learn
            related_skills = await self.find_related_skills(missing_skill)
            
            # Find prerequisite skills
            prerequisites = []
            for candidate_skill in candidate_skills:
                similarity = await self.calculate_skill_similarity(candidate_skill, missing_skill)
                if similarity > 0.5:
                    prerequisites.append(candidate_skill)
            
            recommendations.append({
                'target_skill': missing_skill,
                'related_skills': related_skills[:5],
                'prerequisites': prerequisites,
                'learning_path': self._create_learning_path(missing_skill, prerequisites)
            })
        
        return recommendations
    
    def _create_learning_path(self, target_skill: str, prerequisites: List[str]) -> List[str]:
        """Create a learning path for a target skill."""
        if target_skill not in self.knowledge_graph:
            return []
        
        # Get skill attributes
        skill_attrs = self.knowledge_graph.nodes[target_skill]
        level = skill_attrs.get('level', 'beginner')
        category = skill_attrs.get('category', 'general')
        
        # Create learning path based on level and category
        learning_path = []
        
        if level == 'beginner':
            learning_path.extend(['Learn basics', 'Practice exercises', 'Build simple projects'])
        elif level == 'intermediate':
            learning_path.extend(['Review fundamentals', 'Advanced concepts', 'Real-world projects'])
        else:  # advanced
            learning_path.extend(['Expert-level concepts', 'Complex projects', 'Mentor others'])
        
        return learning_path
    
    def _calculate_ontology_confidence(self, matches: List[Dict[str, Any]], required_skills: List[str]) -> float:
        """Calculate confidence based on ontology matches."""
        if not required_skills:
            return 0.0
        
        exact_matches = sum(1 for match in matches if match['match_type'] == 'exact')
        semantic_matches = sum(1 for match in matches if match['match_type'] == 'semantic')
        
        total_matches = exact_matches + semantic_matches
        confidence = total_matches / len(required_skills)
        
        return min(1.0, confidence)
    
    async def get_ontology_stats(self) -> Dict[str, Any]:
        """Get ontology statistics."""
        return {
            'total_skills': len([n for n in self.knowledge_graph.nodes() if self.knowledge_graph.nodes[n].get('type') == 'skill']),
            'total_jobs': len([n for n in self.knowledge_graph.nodes() if self.knowledge_graph.nodes[n].get('type') == 'job']),
            'total_relationships': len(self.knowledge_graph.edges()),
            'categories': list(self.skill_ontology.keys()),
            'initialized': self.initialized
        }
    
    async def save_ontology(self, file_path: str):
        """Save ontology to file."""
        try:
            ontology_data = {
                'skill_ontology': self.skill_ontology,
                'job_ontology': self.job_ontology,
                'graph_data': nx.node_link_data(self.knowledge_graph)
            }
            
            with open(file_path, 'w') as f:
                json.dump(ontology_data, f, indent=2)
            
            logger.info(f"Ontology saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving ontology: {e}")

# Global ontology service instance
ontology_service = OntologyService()

async def initialize_ontology_service():
    """Initialize ontology service."""
    await ontology_service.initialize()

async def enhance_candidate_scoring_with_ontology(
    candidate_skills: List[str], 
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Enhance candidate scoring using ontology."""
    return await ontology_service.enhance_candidate_scoring(candidate_skills, job_requirements)

async def find_related_skills(skill: str, max_depth: int = 2) -> List[str]:
    """Find related skills in the knowledge graph."""
    return await ontology_service.find_related_skills(skill, max_depth)

async def get_ontology_stats() -> Dict[str, Any]:
    """Get ontology statistics."""
    return await ontology_service.get_ontology_stats()
