using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace ExamPrep.ViewModels
{
    public partial class QuestionGroupVM
    {   
        public int Id {get; set; }
        public int? ProgramId {get; set;}
        public int? ProgramChapterId { get; set; }
        public int? QuestionTypeId {get: set;}
        public string? LinkToObject {get; set;}
        public string? ObjectType { get; set; }
        public string GroupText {get; set;}
        public string GroupTitle { get; set; }
        public string Explanation { get; set; }
        public DateTime CreatedDate {get; set;} = DateTime.UtcNow;
        
        public virtual ProgramsVM Program {get; set;}
        public virtual QuestionTypeVM QuestionType {get; set;}
        public virtual ICollection<QuestionVM> Questions{get; set;}

    }
}