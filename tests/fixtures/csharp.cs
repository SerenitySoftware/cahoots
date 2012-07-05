// ----------------------------------------------------------------
// * The LOOM.NET project http://rapier-loom.net *
// (C) Copyright by Wolfgang Schult. All rights reserved. 
// This code is licensed under the Apache License 2.0
// To get more information, go to http://loom.codeplex.com/license
// ----------------------------------------------------------------
using System;
using System.Collections.Generic;
using System.Text;
using System.Reflection.Emit;
using System.Reflection;
using System.Linq;

using Loom.CodeBuilder.DynamicProxy.CodeBricks;
using Loom.CodeBuilder.DynamicProxy.DataSlots;
using Loom.JoinPoints.Implementation;
using Loom.CodeBuilder.DynamicProxy.Declarations;

namespace Loom.CodeBuilder.DynamicProxy
{
    /// <summary>
    /// Repr&#228;sentiert einen Konstruktor in der Verwebungsklasse
    /// </summary>
    internal class ProxyConstructorBuilder : ProxyMemberBuilder
    {
        ConstructorBuilder ciimplementation;

        public bool IsAbstract
        {
            get { return ((ProxyTypeBuilder)DeclaringBuilder).IsAbstract; }
        }

        /// <summary>
        /// Baut einen Construktorbuilder
        /// </summary>
        /// <param name="tb"></param>
        /// <param name="jp">der JoinPoint des Konstruktors</param>
        /// <param name="typeisabstract"></param>
        /// <param name="aspectindex"></param>
        public ProxyConstructorBuilder(ProxyTypeBuilder tb, JoinPoint jp, bool typeisabstract, int aspectindex) :
            base(tb, jp)
        {
            if (aspectindex >= 0)
            {
                this.DataSlots.Aspect = new AspectSlot(tb.Declarations.Aspects[aspectindex]);
            }
        }

        public new ProxyConstructorJoinPoint JoinPoint
        {
            get
            {
                return (ProxyConstructorJoinPoint)joinpoint;
            }
        }

        public override MethodBaseJoinPoint BindJoinPointToType()
        {
            return ((IBindConstructor)joinpoint).BindToType(ciimplementation, null, null);
        }

        public ConstructorBuilder Implementation
        {
            get
            {
                return ciimplementation;
            }
        }


        public override void Emit()
        {
            IBaseCtor ibasector = (IBaseCtor)JoinPoint;
            ConstructorInfo targetctor = JoinPoint.ConstructorImplementation;

            Type[] ctorargtypes = ClassObjectImpl.GetCreateMethodArgTypes(targetctor);

            ciimplementation = TypeBuilder.DefineConstructor(targetctor.Attributes, targetctor.CallingConvention, ctorargtypes);
            ilgen = ciimplementation.GetILGenerator();

            // Dataslots initialisieren
            foreach (DataSlot lv in DataSlots)
            {
                lv.EmitInitialization(this);
            }


            // dynamische Aspectfelder initialisieren
            foreach (AspectField aspectfield in Declarations.Aspects.Where(af=>!af.NeedStaticInitialize))
            {
                ilgen.Emit(OpCodes.Ldarg_0);

                // Aspekt aus dem Array holen
                ilgen.Emit(OpCodes.Ldarg_1);
                CommonCode.EmitLdci4(ilgen, aspectfield.ArrayPosition);
                ilgen.Emit(OpCodes.Ldelem_Ref);
                ilgen.Emit(OpCodes.Castclass, DeclaringBuilder.AspectType);

                ilgen.Emit(OpCodes.Stfld, aspectfield.FieldInfo);
            }

            // Die Initializer aufrufen
            IList<ProxyJPInitializerBuilder> initializer = ((ProxyTypeBuilder)DeclaringBuilder).DefinedInitializerBuilder;
            if (initializer != null)
            {
                foreach (ProxyJPInitializerBuilder jpib in initializer)
                {
                    // Hack um dem Initializer den richtigen Joinpoint zu zeigen
                    jpib.SetEmitContext(this);
                    foreach (DataSlot ds in jpib.DataSlots)
                    {
                        ds.EmitInitialization(jpib);
                    }
                    jpib.CodeBrick.Emit(jpib);
                }
            }

            // call base ctor aufrufen, der erste Parameter wird &#252;bersprungen, wenn es kein generierter Konstruktor ist
            ilgen.Emit(OpCodes.Ldarg_0);
            if (ibasector.HasAspectParameter)
            {
                CommonCode.EmitLdArgList(ilgen, 1, ctorargtypes.Length);
            }
            else
            {
                CommonCode.EmitLdArgList(ilgen, 2, ctorargtypes.Length - 1);
            }
            ilgen.Emit(OpCodes.Call, ibasector.BaseCtor);

            ilgen.Emit(OpCodes.Ret);

            ilgen = null;
        }

        public override CodeBrickBuilder DefineAspectCall(System.Reflection.MethodInfo aspectmethod, Loom.JoinPoints.Advice advice)
        {
            System.Diagnostics.Debug.Assert(false);
            return null;
        }

        protected override ContextClassDeclaration GetContextClassDeclaration()
        {
            System.Diagnostics.Debug.Assert(false);
            return null;
        }
    }
}